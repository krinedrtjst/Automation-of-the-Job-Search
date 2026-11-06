"""
Reads all files in input/ (PDF and DOCX), extracts the text from each,
combines everything, and uses the LLM to generate data/resume.json with the maximum
amount of information possible.

Usage:
    python src/scripts/ingest_resume.py
    python src/scripts/ingest_resume.py --provider anthropic
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from dotenv import load_dotenv

load_dotenv()

# Windows consoles default to cp1252, which can't encode ✓/✗ etc. below.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from prompts.job_application_prompts import JSON_STRUCTURE


# ─── Text Extraction ────────────────────────────────────────────────────────

def extract_pdf(path: Path) -> str:
    doc = fitz.open(str(path))
    return "\n".join(page.get_text() for page in doc)


def extract_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def is_legacy_doc(path: Path) -> bool:
    """Word 97-2003 binary format (OLE2 Compound File) vs. zip-based .docx."""
    with open(path, "rb") as f:
        return f.read(8) == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def extract_legacy_doc(path: Path) -> str:
    """Extract text from a binary .doc via antiword (python-docx can't read these)."""
    try:
        result = subprocess.run(
            ["antiword", str(path)],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        print(f"  [ERROR] '{path.name}' is a binary .doc (Word 97-2003) and the "
              f"'antiword' converter was not found in PATH. Install it or "
              f"save the file as .docx and try again.")
        return ""
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] antiword failed on '{path.name}': {e.stderr.decode(errors='replace')}")
        return ""
    return result.stdout.decode("cp1252", errors="replace")


def extract_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    elif suffix == ".doc" and is_legacy_doc(path):
        return extract_legacy_doc(path)
    elif suffix in (".docx", ".doc"):
        return extract_docx(path)
    return ""


def collect_input_texts(input_dir: Path) -> dict[str, str]:
    supported = {".pdf", ".docx", ".doc"}
    texts = {}
    for f in sorted(input_dir.iterdir()):
        if f.suffix.lower() in supported:
            text = extract_file(f)
            if text.strip():
                texts[f.name] = text
                print(f"  ✓ {f.name} ({len(text)} chars)")
    return texts


def load_truth_file(input_dir: Path) -> str:
    truth_path = input_dir / "profile_truth.md"
    if truth_path.exists():
        content = truth_path.read_text(encoding="utf-8")
        print(f"  ✓ profile_truth.md (guardrail loaded)")
        return content
    return ""


# ─── Prompt ───────────────────────────────────────────────────────────────────

def build_prompt(texts: dict[str, str], truth: str = "") -> str:
    sections = "\n\n".join(
        f"### File: {name}\n{text}" for name, text in texts.items()
    )

    truth_block = ""
    if truth:
        truth_block = f"""
## AUTHORITATIVE SOURCE OF TRUTH

The following document was manually curated by the person and is the GROUND TRUTH.
It takes absolute precedence over anything in the resume files below.

CRITICAL RULES when a `profile_truth.md` is provided:
- Any fact stated here overrides the resume files — dates, titles, certifications, levels.
- Items in the "DO NOT INCLUDE" section MUST NOT appear anywhere in the output JSON.
- Fields marked [FILL] mean the person hasn't filled them in yet — leave them empty or omit them; do NOT invent values.
- Education marked "IN PROGRESS" must have no endDate or use the preview year — never treat it as completed.
- Only include certifications explicitly listed here with ✅ or without a status marker.
  Do NOT include certifications marked ❌ or [STATUS] without a confirmed year.

### profile_truth.md
{truth}

---
"""

    return f"""You are an expert resume parser and career data analyst.
{truth_block}
## RESUME FILES

Below are the contents of {len(texts)} resume file(s) belonging to the same person.
They may be different versions of the same resume (general, specialized per role, etc.).

Your task:
1. Read ALL versions carefully.
2. Extract the most complete, accurate picture of this person's career.
3. When the same information appears in multiple versions, use the most detailed one.
4. When specialized versions add skills or highlights not in the general version, INCLUDE them.
5. If a profile_truth.md was provided above, it is the authoritative source — reconcile conflicts in its favor.
6. Output a single, comprehensive resume as a valid JSON object.

Use EXACTLY this JSON schema — do not add or remove top-level keys:
{JSON_STRUCTURE}

Rules:
- Use the actual person's data. Do not invent anything.
- `basics.summary`: write a neutral, comprehensive 3-sentence professional summary.
- `work[].highlights`: include ALL bullet points found across all versions (deduplicated).
- `skills`: merge all skill categories across versions; keep the most complete keyword lists.
- Dates must be in "YYYY-MM" format (e.g., "2020-03"). Use "Present" for current roles.
- Output ONLY the JSON object — no markdown, no explanation, no code fences.

---

{sections}
"""


# ─── LLM call ─────────────────────────────────────────────────────────────────

def call_llm(prompt: str, provider: str) -> str:
    from src.llm_factory import get_llm

    llm = get_llm(provider=provider, temperature=0.1, purpose="extraction")
    return llm.call(prompt)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Converts resumes from input/ to data/resume.json"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "gemini", "grok", "bedrock"],
        default=None,
        help="LLM Provider (default: LLM_PROVIDER from .env)",
    )
    parser.add_argument(
        "--person",
        default=os.getenv("PERSON", "dev_procurando"),
        help="Who to generate the resume.json for (e.g., dev_procurando). Default: PERSON in .env, or 'dev_procurando'",
    )
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Directory with resume files (default: input/<person>/)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: data/<person>/resume.json)",
    )
    args = parser.parse_args()

    args.input_dir = args.input_dir or f"input/{args.person}"
    args.output = args.output or f"data/{args.person}/resume.json"

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"[ERROR] Directory '{input_dir}' not found.")
        sys.exit(1)

    print(f"\nReading files from '{input_dir}/'...")
    texts = collect_input_texts(input_dir)
    if not texts:
        print("[ERROR] No PDF or DOCX file found in input/")
        sys.exit(1)

    truth = load_truth_file(input_dir)

    print(f"\nSending {len(texts)} file(s) to the LLM...")
    prompt = build_prompt(texts, truth=truth)
    raw = call_llm(prompt, provider=args.provider)

    # Clean potential code fences added by the LLM by mistake
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()
    
    # Also strip "json" identifier if present right after the code fence
    if cleaned.startswith("json\n"):
        cleaned = cleaned[5:].strip()

    try:
        resume_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] The LLM returned invalid JSON: {e}")
        print("Saving raw response to data/resume_raw.txt for inspection...")
        Path("data/resume_raw.txt").write_text(raw, encoding="utf-8")
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(resume_data, indent=2, ensure_ascii=False), encoding="utf-8")

    name = resume_data.get("basics", {}).get("name", "—")
    print(f"\n✓ resume.json generated successfully!")
    print(f"  Detected name  : {name}")
    print(f"  Experiences    : {len(resume_data.get('work', []))}")
    print(f"  Skills         : {len(resume_data.get('skills', []))}")
    print(f"  Certifications : {len(resume_data.get('certificates', []))}")
    print(f"  Projects       : {len(resume_data.get('projects', []))}")
    print(f"  Saved at       : {output_path}")


if __name__ == "__main__":
    main()