import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()

# Assuming your updated identity as the default
DEFAULT_PERSON = os.getenv("PERSON", "karine_justino")


def list_people() -> List[str]:
    """Returns a list of all subdirectories (people profiles) in the data folder."""
    data_dir = Path("data")
    if not data_dir.exists():
        return []
    return sorted(d.name for d in data_dir.iterdir() if d.is_dir())


def list_roles(person: str) -> List[str]:
    """Returns a list of target job profiles (.txt) available for a specific person."""
    profiles_dir = Path(f"data/{person}/job_profiles")
    if not profiles_dir.exists():
        return []
    return sorted(f.stem for f in profiles_dir.glob("*.txt"))


def prepare_output_dir(person: str, role: str, base_resume_path: str) -> str:
    """
    Creates the output directory structure for a specific role and seeds it 
    with the canonical base resume.
    """
    output_dir = Path(f"outputs/{person}/{role}")
    
    for subdir in ("json", "latex", "pdf"):
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)
        
    dst = output_dir / "json" / "resume.json"
    
    # If the best-match resume is the output dir itself (re-run), refresh from canonical source
    if Path(base_resume_path).resolve() == dst.resolve():
        base_resume_path = f"data/{person}/resume.json"
        
    shutil.copy(base_resume_path, dst)
    return str(output_dir)


def run_for_role(person: str, role: str, provider: str = None, language: str = "pt-BR"):
    """Runs the full CrewAI pipeline against a specific, predefined role profile."""
    profile_path = Path(f"data/{person}/job_profiles/{role}.txt")
    if not profile_path.exists():
        print(f"[ERROR] Target profile not found: {profile_path}")
        available = ", ".join(list_roles(person)) or "None"
        print(f"  Available profiles for '{person}': {available}")
        sys.exit(1)

    original_resume_path = f"data/{person}/resume.json"
    output_dir = prepare_output_dir(person, role, base_resume_path=original_resume_path)

    # Late import to prevent slow CLI startup times
    from src.agents.job_application_crew import JobApplicationCrew

    crew = JobApplicationCrew(
        role=role,
        job_profile_path=str(profile_path),
        output_dir=output_dir,
        provider=provider,
        language=language,
        original_resume_path=original_resume_path,
    )
    return crew.run()


def run_for_job_desc(person: str, job_desc_path: str, provider: str = None, language: str = "pt-BR"):
    """
    Runs the pipeline against a specific job description file (.md), dynamically 
    matching it against previously generated resumes to use as a starting point.
    """
    path = Path(job_desc_path)
    if not path.exists():
        print(f"[ERROR] Job description file not found: {job_desc_path}")
        sys.exit(1)

    from src.scripts.resume_matcher import extract_job_title, find_best_resume
    from src.scripts.update_tracker import log_application

    job_desc = path.read_text(encoding="utf-8")
    role_name = extract_job_title(job_desc)
    
    print(f"\n{'='*60}")
    print(f"  Person: {person} | Identified Role: {role_name}")
    print(f"{'='*60}")

    original_resume_path = f"data/{person}/resume.json"

    # Search for the best existing resume to use as a baseline
    match = find_best_resume(job_desc, outputs_dir=f"outputs/{person}")
    if match:
        match_path, match_score, match_folder = match
        base_resume = match_path
        print(f"\n[INFO] Best matching resume found:")
        print(f"       outputs/{person}/{match_folder}/  (Overlap score: {match_score:.0%})")
        print(f"[INFO] Using it as the baseline for this application.\n")
    else:
        base_resume = original_resume_path
        print(f"\n[INFO] No suitable existing resume found. Using the canonical original resume.\n")

    output_dir = prepare_output_dir(person, role_name, base_resume_path=base_resume)

    from src.agents.job_application_crew import JobApplicationCrew

    crew = JobApplicationCrew(
        role=role_name,
        job_profile_path=str(path),
        output_dir=output_dir,
        provider=provider,
        language=language,
        original_resume_path=original_resume_path,
    )
    
    # Run the crew, then trigger the automated CSV tracker
    result = crew.run()
    log_application(person, role_name, output_dir)
    return result


def run_legacy(person: str, provider: str = None):
    """Backwards-compatible run using data/<person>/job_desc.txt → outputs/<person>."""
    output_dir = Path(f"outputs/{person}")
    
    for subdir in ("json", "latex", "pdf"):
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)
        
    original_resume_path = Path(f"data/{person}/resume.json")
    shutil.copy(original_resume_path, output_dir / "json" / "resume.json")

    from src.agents.job_application_crew import JobApplicationCrew

    crew = JobApplicationCrew(
        job_profile_path=f"data/{person}/job_desc.txt",
        output_dir=str(output_dir),
        provider=provider,
        original_resume_path=str(original_resume_path),
    )
    return crew.run()


def main():
    # CrewAI emits Unicode tool events even on Windows consoles using cp1252.
    for output in (sys.stdout, sys.stderr):
        if hasattr(output, "reconfigure"):
            output.reconfigure(encoding="utf-8", errors="replace")
            
    parser = argparse.ArgumentParser(
        prog="career-command-center",
        description="AI Career Automation Command Center — Resume Repositioning & Application Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py --person {DEFAULT_PERSON} --role data_scientist
  python main.py --role ai_engineer --provider anthropic      # uses PERSON from .env (default: {DEFAULT_PERSON})
  python main.py --job                                        # uses input/<person>/job_desc.md
  python main.py --job input/senior_vacancy.md                # points to a specific file
  python main.py --all
  python main.py --all --person {DEFAULT_PERSON}
  python main.py --list-roles --person {DEFAULT_PERSON}
  python main.py --list-people
        """,
    )
    parser.add_argument(
        "--person",
        metavar="PERSON",
        default=DEFAULT_PERSON,
        help=f"Target person profile (e.g., karine_justino). Default: PERSON in .env, or '{DEFAULT_PERSON}'",
    )
    parser.add_argument(
        "--role",
        metavar="ROLE",
        help="Target job profile (e.g., data_scientist, ai_engineer). Reads from data/<person>/job_profiles/<role>.txt",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Batch generate optimized resumes for ALL available roles",
    )
    parser.add_argument(
        "--provider",
        metavar="PROVIDER",
        choices=["openai", "anthropic", "gemini", "grok", "bedrock"],
        help="LLM Provider (default: value of LLM_PROVIDER in .env, or openai)",
    )
    parser.add_argument(
        "--job",
        metavar="PATH",
        nargs="?",
        const="__default__",
        help="Markdown file containing the job description (default: input/<person>/job_desc.md)",
    )
    parser.add_argument(
        "--lang",
        metavar="LANG",
        default="pt-BR",
        help="Language of the generated resume: 'pt-BR' (default) or 'en' for English",
    )
    parser.add_argument(
        "--list-roles",
        action="store_true",
        help="List available job profiles in data/<person>/job_profiles/",
    )
    parser.add_argument(
        "--list-people",
        action="store_true",
        help="List available person profiles (subdirectories in data/)",
    )

    args = parser.parse_args()
    person = args.person

    if args.list_people:
        people = list_people()
        if people:
            print("Available person profiles:")
            for p in people:
                print(f"  - {p}")
        else:
            print("No profiles found in the data/ directory.")
        return

    if args.list_roles:
        roles = list_roles(person)
        if roles:
            print(f"Available job profiles for '{person}':")
            for r in roles:
                print(f"  - {r}")
        else:
            print(f"No job profiles found in data/{person}/job_profiles/")
            print("Create .txt files in that directory for each target role.")
        return

    if args.all:
        roles = list_roles(person)
        if not roles:
            print(f"[ERROR] No job profiles found in data/{person}/job_profiles/")
            sys.exit(1)
            
        print(f"Executing batch run for {person} — {len(roles)} profile(s): {', '.join(roles)}\n")
        for role in roles:
            print(f"\n{'='*60}")
            print(f"  Processing Role: {role}")
            print(f"{'='*60}\n")
            run_for_role(person, role, provider=args.provider, language=args.lang)
        return

    if args.role:
        run_for_role(person, args.role, provider=args.provider, language=args.lang)
        return

    if args.job is not None:
        job_path = f"input/{person}/job_desc.md" if args.job == "__default__" else args.job
        run_for_job_desc(person, job_path, provider=args.provider, language=args.lang)
        return

    # Default fallback: legacy mode
    print(f"[INFO] No --role or --job specified. Running legacy mode using data/{person}/job_desc.txt.")
    run_legacy(person, provider=args.provider)


if __name__ == "__main__":
    main()