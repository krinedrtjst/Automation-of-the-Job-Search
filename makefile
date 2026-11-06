# Makefile — AI Career Automation Command Center

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = uv pip

# Default target when just typing 'make'
.PHONY: help
help:
	@echo "======================================================================"
	@echo " AI Career Automation Command Center - Makefile"
	@echo "======================================================================"
	@echo ""
	@echo "Usage:"
	@echo "  make setup         - Create virtual environment and install dependencies via uv"
	@echo "  make run           - Run the main pipeline (default legacy mode)"
	@echo "  make role ROLE=x   - Run pipeline for a specific role (e.g., ROLE=data_scientist)"
	@echo "  make all-roles     - Run pipeline for all available roles in batch"
	@echo "  make job JOB=path  - Run pipeline for a specific job description .md file"
	@echo "  make ingest        - Parse PDFs in input/ and generate base data/resume.json"
	@echo "  make compare       - Generate visual diff PDF between original and tailored resume"
	@echo "  make linkedin-auth - Refresh LinkedIn OAuth tokens"
	@echo "  make clean         - Remove LaTeX build artifacts and __pycache__ folders"
	@echo ""

.PHONY: setup
setup:
	uv venv $(VENV) --python 3.12
	$(PIP) install -r requirements.txt

.PHONY: run
run:
	$(PYTHON) main.py

.PHONY: role
# Usage: make role ROLE=data_scientist [PROVIDER=anthropic]
role:
	@if [ -z "$(ROLE)" ]; then echo "[ERROR] ROLE is not defined. Use: make role ROLE=<role_name>"; exit 1; fi
	$(PYTHON) main.py --role $(ROLE) $(if $(PROVIDER),--provider $(PROVIDER),)

.PHONY: all-roles
# Usage: make all-roles [PROVIDER=anthropic]
all-roles:
	$(PYTHON) main.py --all $(if $(PROVIDER),--provider $(PROVIDER),)

.PHONY: job
# Usage: make job JOB=input/karine_justino/vaga.md [PROVIDER=anthropic]
job:
	$(PYTHON) main.py --job $(if $(JOB),$(JOB),) $(if $(PROVIDER),--provider $(PROVIDER),)

.PHONY: list-roles
list-roles:
	$(PYTHON) main.py --list-roles

.PHONY: ingest
# Reads input/ directory and generates the authoritative data/resume.json
# Usage: make ingest [PROVIDER=anthropic]
ingest:
	$(PYTHON) src/scripts/ingest_resume.py $(if $(PROVIDER),--provider $(PROVIDER),)

.PHONY: render
render:
	$(PYTHON) resume/generator.py

.PHONY: compare
compare:
	$(PYTHON) src/scripts/run_compare_pdf.py

.PHONY: linkedin-auth
linkedin-auth:
	$(PYTHON) src/scripts/linkedin_auth.py

.PHONY: clean
clean:
	@echo "Cleaning LaTeX artifacts and Python caches..."
	@find . -type f \( -name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.fls" -o -name "*.fdb_latexmk" -o -name "*.synctex.gz" -o -name "*.toc" \) -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Clean complete."