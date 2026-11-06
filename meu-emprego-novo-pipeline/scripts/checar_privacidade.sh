#!/usr/bin/env bash
# Scans for potential personal data in versionable repository files.
# Usage: bash scripts/check_privacy.sh
# Output: exits with 0 if clean; exits with 1 if suspicious data is found.

set -u
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root_dir" || exit 2

# Files candidate for commit, strictly ignoring private/ and .git/ directories
files=$(find . -type f \
  -not -path "./.git/*" -not -path "./private/*" -not -path "./input/*" -not -path "./outputs/*" -not -path "./data/*" \
  -not -name "*.pdf" -not -name "check_privacy.sh" \
  \( -name "*.md" -o -name "*.json" -o -name "*.tex" -o -name "*.csv" -o -name "*.py" -o -name "*.txt" \))

found_issue=0

check_pattern() {
  local label="$1" pattern="$2" exception="${3:-}"
  local result
  result=$(echo "$files" | xargs grep -nEH "$pattern" 2>/dev/null)
  if [ -n "$exception" ]; then
    result=$(echo "$result" | grep -vE "$exception")
  fi
  if [ -n "$result" ]; then
    echo "== Alert: $label =="
    echo "$result"
    echo
    found_issue=1
  fi
}

# Emails excluding placeholder examples and approved professional email
check_pattern "Real Email" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' '@exemplo\.com|@example\.com|your\.email@|karineduartejustino@proton\.me'
# Brazilian Phone Numbers
check_pattern "Phone Number" '\(?[0-9]{2}\)?[ -]?9?[0-9]{4}-?[0-9]{4}'
# Brazilian CPF (ID Document)
check_pattern "CPF (ID)" '[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}'
# LinkedIn Profiles excluding placeholders and approved profiles
check_pattern "LinkedIn Profile" 'linkedin\.com/in/[A-Za-z0-9_-]+' 'your-profile|ana-souza-example|karinedjustino'

if [ "$found_issue" -eq 0 ]; then
  echo "OK: No obvious personal data found in public files."
  echo "Reminder: Always manually review your files before committing to the repository."
  exit 0
fi

echo "ACTION REQUIRED: Review the items flagged above before committing."
exit 1