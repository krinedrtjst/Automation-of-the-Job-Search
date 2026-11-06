#!/usr/bin/env python3
"""
Generates a visual comparison (diff) between two PDF resumes.
"""

import sys
import argparse
import logging
from pathlib import Path

# 1. Elegant path resolution using pathlib
# Instead of polluting sys.path with multiple parent directories, 
# we dynamically find the project root and insert it once.
# (Adjust .parents[2] to .parents[1] if this script is only one folder deep)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2] 

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now we can safely import from the tools package
from tools.tools_utils import generate_comparison_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Generate a visual diff between two PDF resumes.")
    parser.add_argument(
        "--original", 
        default="outputs/pdf/original_long_resume.pdf", 
        help="Path to the original PDF"
    )
    parser.add_argument(
        "--modified", 
        default="outputs/pdf/output_resume.pdf", 
        help="Path to the modified PDF"
    )
    parser.add_argument(
        "--output", 
        default="outputs/pdf/compare_diff.pdf", 
        help="Path to save the diff PDF"
    )
    
    args = parser.parse_args()
    
    original_path = Path(args.original)
    modified_path = Path(args.modified)
    output_path = Path(args.output)
    
    # 2. Safety checks before executing
    if not original_path.exists():
        logging.error(f"Original PDF not found: {original_path}")
        sys.exit(1)
        
    if not modified_path.exists():
        logging.error(f"Modified PDF not found: {modified_path}")
        sys.exit(1)
        
    # Ensure the output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"Comparing '{original_path.name}' and '{modified_path.name}'...")
    
    try:
        generate_comparison_pdf(str(original_path), str(modified_path), str(output_path))
        logging.info(f"Comparison PDF successfully generated at: {output_path}")
    except Exception as e:
        logging.error(f"Failed to generate comparison PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()