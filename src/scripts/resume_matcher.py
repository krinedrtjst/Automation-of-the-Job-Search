"""
resume_matcher.py — extracts a job title from a job description and finds the 
most aligned resume among those already generated in the outputs/ directory.
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional


# ── Utilities ───────────────────────────────────────────────────────────────

def slugify(text: str, max_len: int = 60) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")[:max_len]


# ── Title Extraction ────────────────────────────────────────────────────────

_TITLE_PATTERNS = [
    # PT-BR (Adapted for Data & AI)
    r"(Cientista\s+(?:de\s+)?[^\n,\.]{3,50})",
    r"(Desenvolvedor[a]?\s+[^\n,\.]{3,50})",
    r"(Analista\s+(?:de\s+)?[^\n,\.]{3,50})",
    r"(Especialista\s+(?:em\s+)?[^\n,\.]{3,50})",
    r"(Engenheiro[a]?\s+(?:de\s+)?[^\n,\.]{3,50})",
    r"(Arquiteto[a]?\s+(?:de\s+)?[^\n,\.]{3,50})",
    r"(Consultor[a]?\s+(?:de\s+)?[^\n,\.]{3,50})",
    r"(Senior\s+[^\n,\.]{3,50})",
    r"(Tech Lead[^\n,\.]{0,40})",
    # English (Adapted for Data & AI)
    r"(?:work|position|role|hiring|seeking|looking for)\s+as\s+(?:a|an)\s+([\w][\w\s]{4,55}?)(?:\.|,|\n|$)",
    r"((?:Senior|Junior|Lead|Staff|Principal)\s+[\w\s]{3,45}?(?:Scientist|Developer|Engineer|Architect|Analyst|Consultant|Manager))",
    r"([\w\s]{3,40}?(?:Scientist|Developer|Engineer|Architect|Analyst|Consultant|Manager))\s+role",
]

# Technologies that, if found in the job description, help name the folder.
# Strictly adapted to Karine's stack (Data Science, NLP, ML Ops).
_TECH_KEYWORDS = [
    "PySpark", "PyTorch", "Transformers", "LLM", "RLHF", "LangChain", 
    "TensorFlow", "spaCy", "NLTK", "Machine Learning", "NLP", "AI Alignment",
    "Power BI", "Tableau", "Databricks", "Snowflake", "SQL", "BigQuery",
]

_GENERIC_HEADERS = {
    "descricao da vaga", "descrição da vaga", "detalhes da vaga",
    "sobre a vaga", "sobre a oportunidade", "vaga", "job description",
    "cargo", "posição", "oportunidade", "role", "requirements",
}

_TRAILING_PREP = re.compile(
    r'\s+(e|de|da|do|para|com|em|no|na|os|as|um|uma|of|in|for|with)\s*$', re.IGNORECASE
)


def _is_generic(line: str) -> bool:
    return slugify(line) in _GENERIC_HEADERS


def extract_job_title(job_desc: str) -> str:
    """
    Extracts a short job title from the job description text.
    Attempt order:
      1. Direct job patterns in PT-BR/EN (Data Scientist, ML Engineer...)
      2. Short line containing a known technology + inferred role
      3. First mentioned technology as a prefix
      4. First non-generic, reasonably short line
    """
    # 1. Direct job patterns
    for pattern in _TITLE_PATTERNS:
        m = re.search(pattern, job_desc, re.IGNORECASE)
        if m:
            title = _TRAILING_PREP.sub("", m.group(1).strip()).strip()
            slug = slugify(title)
            if len(slug) >= 4:
                return slug

    # 2. Short line (10–80 chars) that contains known tech and is not generic
    for line in job_desc.splitlines():
        clean = line.strip().lstrip("#").strip()
        if 10 <= len(clean) <= 80 and not _is_generic(clean):
            for tech in _TECH_KEYWORDS:
                if tech.lower() in clean.lower():
                    return slugify(clean)

    # 3. Company Name (ALL CAPS line) + first found technology
    company = None
    first_tech = None
    for line in job_desc.splitlines():
        clean = line.strip()
        if re.match(r'^[A-Z][A-Z0-9 \-&\.]{4,}$', clean) and not company:
            company = clean.split()[0].capitalize()
        if first_tech is None:
            for tech in _TECH_KEYWORDS:
                if tech.lower() in clean.lower():
                    first_tech = tech
                    break
        if company and first_tech:
            break
            
    if first_tech:
        return slugify(first_tech)

    # 4. Fallback: first non-generic line
    for line in job_desc.splitlines():
        clean = line.strip().lstrip("#").strip()
        if 5 <= len(clean) <= 80 and not _is_generic(clean):
            return slugify(clean)

    return "vaga"


# ── Keyword Overlap Matching ────────────────────────────────────────────────

_PT_STOPWORDS = {
    # PT-BR
    "para", "como", "mais", "uma", "com", "que", "por", "nos", "nas",
    "dos", "das", "pelo", "pela", "seus", "suas", "esse", "essa", "este",
    "esta", "são", "será", "deve", "pode", "nossa", "nosso", "você",
    "aqui", "onde", "também", "além", "sobre", "quando", "todos", "cada", "novo",
    # English generic
    "time", "team", "role", "work", "about", "across", "ability", "abilities",
    "advanced", "agile", "agreed", "alongside", "americas", "attention", "attitude",
    "average", "based", "best", "build", "career", "challenge", "client", "clients",
    "commitment", "commitments", "companies", "company", "competitive", "connect",
    "consistently", "continuing", "daily", "deliver", "design", "detail", "diverse",
    "education", "empower", "ensure", "environment", "every", "existing", "expand",
    "experience", "fair", "find", "flexible", "focus", "fostering", "global",
    "great", "grow", "growth", "high", "hiring", "hours", "inclusive", "individual",
    "individuals", "innovative", "integrate", "into", "issue", "issues", "join",
    "large", "leading", "level", "library", "looking", "match", "meaningful",
    "mindset", "network", "opportunities", "opportunity", "over", "ownership",
    "perform", "performance", "positive", "prioritizing", "professional",
    "professionals", "project", "projects", "provide", "remote", "required",
    "respectful", "skilled", "skills", "software", "startup", "startups",
    "supportive", "talent", "teams", "their", "them", "they", "this", "through",
    "tools", "transparency", "transparent", "trusted", "using", "various",
    "week", "welcome", "where", "while", "with", "within", "worldwide", "year", "years",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r'\b[a-z][a-z0-9+#\.]{2,}\b', text.lower())
    return {w for w in words if w not in _PT_STOPWORDS and len(w) >= 4}


def _resume_text(resume: dict) -> str:
    parts = []
    basics = resume.get("basics", {})
    parts.append(basics.get("summary", ""))
    parts.append(basics.get("label", ""))
    for skill in resume.get("skills", []):
        parts.append(skill.get("name", ""))
        parts.extend(skill.get("keywords", []))
    for job in resume.get("work", []):
        parts.append(job.get("position", ""))
        parts.extend(job.get("highlights", []))
    return " ".join(parts)


def score_resume(resume: dict, job_desc: str) -> float:
    """Returns [0, 1] — proportion of job keywords present in the resume."""
    job_kw = _keywords(job_desc)
    if not job_kw:
        return 0.0
    resume_kw = _keywords(_resume_text(resume))
    return len(job_kw & resume_kw) / len(job_kw)


# ── Best Resume Search ──────────────────────────────────────────────────────

def find_best_resume(
    job_desc: str,
    outputs_dir: str = "outputs",
    exclude_folder: Optional[str] = None,
    min_score: float = 0.06,
) -> Optional[tuple[str, float, str]]:
    """
    Scans outputs/<*>/json/resume.json and returns the most aligned to the job description.

    Returns:
        (path, score, folder_name) or None if no candidate is found
        with a score >= min_score.
    """
    base = Path(outputs_dir)
    if not base.exists():
        return None

    best_path: Optional[str] = None
    best_score = -1.0
    best_folder: Optional[str] = None

    for candidate in sorted(base.glob("*/json/resume.json")):
        folder = candidate.parent.parent.name
        if folder == exclude_folder:
            continue
        try:
            resume = json.loads(candidate.read_text(encoding="utf-8"))
            s = score_resume(resume, job_desc)
            if s > best_score:
                best_score = s
                best_path = str(candidate)
                best_folder = folder
        except Exception:
            continue

    if best_path and best_score >= min_score:
        return (best_path, best_score, best_folder)
    return None