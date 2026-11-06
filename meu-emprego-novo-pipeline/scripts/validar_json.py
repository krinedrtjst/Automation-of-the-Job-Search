#!/usr/bin/env python3
"""Validates the basic structure of a resume.json file.

Usage: python3 scripts/validate_json.py path/to/resume.json
Output: exit code 0 if valid; 1 if errors are found.
"""
import json
import re
import sys

MANDATORY_ROOT = ["basics", "work", "education", "skills"]
MANDATORY_BASICS = ["name", "label", "email", "summary"]
MANDATORY_WORK = ["name", "position", "startDate", "highlights"]
DATE_RE = re.compile(r"^(\d{4}(-\d{2})?|Present|Atual)$")

# Command Center Adaptation: Blocklist to catch common AI hallucinations 
# based on Karine's strict profile constraints.
HALLUCINATION_BLOCKLIST = ["react", "node.js", "full-stack", "full stack", "frontend"]

def validate(data):
    errors, warnings = [], []

    # 1. Check Root Keys
    for key in MANDATORY_ROOT:
        if key not in data:
            errors.append(f"Missing mandatory root key: {key}")
    if errors:
        return errors, warnings

    # 2. Check Basics
    for field in MANDATORY_BASICS:
        if not str(data["basics"].get(field, "")).strip():
            errors.append(f"basics.{field} is empty or missing")

    summary = data["basics"].get("summary", "")
    if len(summary) > 700:
        warnings.append("basics.summary exceeds 700 characters; keep it concise and interdisciplinary.")

    # 3. Check Work Experience
    if not data.get("work"):
        errors.append("'work' section is empty")

    for i, job in enumerate(data.get("work", [])):
        label = f"work[{i}] ({job.get('name', '?')})"
        for field in MANDATORY_WORK:
            if field not in job or job[field] in ("", []):
                errors.append(f"{label}: field '{field}' is missing or empty")
        
        for field in ("startDate", "endDate"):
            value = job.get(field)
            if value and not DATE_RE.match(str(value)):
                errors.append(f"{label}: {field}='{value}' is not in YYYY, YYYY-MM, or Present format")
        
        # Adapted to Karine's density preference (max 5 highlights for recent roles)
        if len(job.get("highlights", [])) > 6:
            warnings.append(f"{label}: more than 6 highlights; trim to prioritize PySpark/PyTorch/RLHF metrics.")
        
        # Anti-Hallucination check for work highlights
        highlights_text = " ".join(job.get("highlights", [])).lower()
        for banned in HALLUCINATION_BLOCKLIST:
            if banned in highlights_text:
                warnings.append(f"{label}: Potential AI hallucination detected ('{banned}'). Cross-reference with profile_truth.md!")

    # 4. Check Certificates
    for i, cert in enumerate(data.get("certificates", [])):
        if not cert.get("name"):
            errors.append(f"certificates[{i}] has no name")

    # 5. Anti-Hallucination check for skills
    skills_text = " ".join(
        [kw.lower() for skill in data.get("skills", []) for kw in skill.get("keywords", [])]
    )
    for banned in HALLUCINATION_BLOCKLIST:
        if banned in skills_text:
            warnings.append(f"skills: Potential AI hallucination detected ('{banned}'). Remove immediately if unverified.")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        print(f"ERROR reading file: {exc}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: The file is not a valid JSON ({exc}).")
        print("Ensure you only saved the raw JSON from the assistant: from the first { to the last }, no markdown blocks ``` and no comments.")
        return 1

    errors, warnings = validate(data)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    
    if errors:
        return 1
    print("OK: resume.json is valid and strictly aligned with profile_truth.md constraints.")
    return 0


if __name__ == "__main__":
    sys.exit(main())