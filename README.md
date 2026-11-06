---

# AI Career Automation Command Center

**An open-source methodology and AI-powered CLI toolkit designed to automate the most repetitive parts of the job search process.**

> As a Data Scientist and AI Alignment Specialist transitioning into senior roles, I decided to treat the job search exactly like an ETL pipeline: raw data comes in, gets processed programmatically, and strict guardrails ensure the final output is highly accurate.
> This repository contains the methodology and the automated Command Center I built to tailor my resume for every application without hallucinating or losing control of my narrative.

Here you will find two things:

1. **The Methodology:** A structured, step-by-step guide to organizing your job search—from building a Master Profile to running retrospective cycles. It works with any AI assistant.
2. **The Tool:** A Python CLI powered by an autonomous crew of AI agents that automates the most labor-intensive part of the process: generating a tailored, ATS-optimized PDF resume for every single job description.

---

## Table of Contents

1. [The Methodology at a Glance](#1-the-methodology-at-a-glance)
2. [Choose Your Path](#2-choose-your-path)
3. [Three Critical Warnings Before Starting](#3-three-critical-warnings-before-starting)
4. [Path A: Methodology via Chat Assistant](#4-path-a-methodology-via-chat-assistant)
5. [Path B: Automating with the CLI Command Center](#5-path-b-automating-with-the-cli-command-center)
6. [Repository Structure](#6-repository-structure)
7. [Contributing & License](#7-contributing--license)
8. [About the Author](#8-about-the-author)

---

## 1. The Methodology at a Glance

Job hunting is a volume game: dozens of vacancies, each requiring slightly different phrasing, followed by predictable interview questions. This method treats the process like a **data pipeline**, where each stage feeds into the next:


```

PREPARE      establish ground rules → master profile → LinkedIn            once
│
▼
FIND         search for roles → filter & triage                            in cycles
│
▼
APPLY        tailor resume → coverage review                               for each selected role
→ interview prep → apply & log
│
▼
LEARN        what generated responses? adjust profile & prompts            weekly, then back to FIND

```

Three principles support this entire framework:

1. **A Single Source of Truth:** You write the long, honest, comprehensive version of your career exactly once in `profile_truth.md`. Every resume and interview answer is derived exclusively from this file.
2. **AI Proposes, You Decide:** The AI can reorder, summarize, and translate. It **cannot** invent. Nothing goes out with your name on it without your final review.
3. **Log to Learn:** A simple CSV tracker shows which resumes and job boards yield responses.

---

## 2. Choose Your Path

Both paths follow the same methodology. The difference is **who physically builds the resume**.

|  | Path A: AI Chat Assistant | Path B: Agentic CLI (The Command Center) |
| --- | --- | --- |
| **How it works** | You copy-paste provided prompts into ChatGPT/Claude | You run a Python command, and a crew of AI agents generates the files |
| **Best for** | Non-technical professionals or quick starts | Tech professionals who want to automate bulk resume generation |
| **Requirements** | Any AI assistant, Python 3.9+, LaTeX | Python 3.12, an LLM API Key (OpenAI/Anthropic) |
| **Cost** | Your chat subscription | API consumption per run |
| **Start at** | [Section 4](#4-path-a-methodology-via-chat-assistant) | [Section 5](#5-path-b-automating-with-the-cli-command-center) |

**Unsure? Start with Path A.** The Master Profile you write for Path A is the exact same file required by the CLI in Path B.

---

## 3. Three Critical Warnings Before Starting

**1. Your Data is Yours.** A resume is personal data. Everything you put in a prompt is sent to an LLM provider.

- Folders like `input/`, `data/`, `outputs/`, and `private/` are deliberately listed in `.gitignore`. Never commit them.
- API keys live exclusively in `.env`.
- Do not write anything in your Master Profile that you are uncomfortable sending to an API. Passwords, IDs, and financial data have no place here.

**2. You are Responsible for the Output.** The **Zero-Hallucination Policy** reduces AI fabrications significantly, but it does not eliminate them. The AI might still confuse dates or swap numbers. You must read the final PDF before clicking apply.

**3. Recruitment Scams are Real.** Never accept an interview that asks you to download and run compiled code locally, nor one that demands your passport details upfront. Read the Security Guide (in the `docs/` folder) before your first application.

> *Disclaimer: This project is strictly for reframing real, truthful experience. It is not designed to fabricate skills, bypass background checks, or mass-spam job boards.*

---

## 4. Path A: Methodology via Chat Assistant

*(See full tutorial in the `docs/` folder)*

---

## 5. Path B: Automating with the CLI Command Center

> **Built by an AI Engineer, for Tech Professionals.** This is not a polished SaaS; it is a hackable CLI. Every prompt, agent, and template is exposed code you can modify.

### How the CLI Works

You drop your old PDF resumes and your `profile_truth.md` into an input folder. You provide a job description. The AI agents (built on [CrewAI](https://docs.crewai.com)) read the data, debate the best strategy, evaluate the result against the vacancy, and output a tailored PDF.


```

input//    PDF/DOCX resumes + profile_truth.md
│
▼
data//resume.json   ← Your base data; agents never alter this file
│  + Job Description
▼
5 Agents: Strategist → HR Evaluator ⇄ Editor → Reporter → Interview Coach
▼
outputs///    JSON, LaTeX, PDF + Reviews & Interview Prep

```

### Step 1: Install

**Requirements:** Python 3.12 and an API Key. LaTeX (`pdflatex`) is recommended for the advanced template; without it, the CLI falls back to a simpler PDF generator using `reportlab`.

```bash
git clone [https://github.com/krinedrtjst/career-command-center.git](https://github.com/krinedrtjst/career-command-center.git)
cd career-command-center
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

```

### Step 2: Choose Your AI Provider

Open `.env` and configure your API keys. **The default is `openai**`.

| `LLM_PROVIDER` | API Key Required | Default Model |
| --- | --- | --- |
| `openai` | `OPENAI_API_KEY` | GPT-4o |
| `anthropic` | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet |
| `gemini` | `GOOGLE_API_KEY` | Gemini 1.5 Pro |

### Step 3: Prepare Your Data

1. **Create your folder.** Choose an identifier (e.g., `karine_justino`) and place your old PDF resumes inside:

```bash
mkdir -p input/karine_justino

```

2. **Write your `profile_truth.md**` in `input/karine_justino/`. This is the Ground Truth. Add a `## DO NOT INCLUDE` section for things the AI is strictly forbidden from adding (e.g., frontend frameworks you don't want to work with).
3. **Generate the base JSON:**

```bash
make ingest PERSON=karine_justino

```

4. **Review `data/karine_justino/resume.json`.** This is the master database the agents will use. Fix any extraction errors manually.

### Step 4: Generate a Tailored Resume

1. Save the target Job Description to `input/karine_justino/job_desc.md`.
2. Run the Command Center:

```bash
make job JOB=input/karine_justino/job_desc.md

```

3. Retrieve your results in `outputs/karine_justino/<role_name>/`. You will find:

* `output_resume.pdf` (Your ready-to-send resume)
* `rating_report.md` (The HR Agent's critique and score out of 10)
* `interview_prep.md` (Custom STAR-method interview answers based on your experience)

### Working with Job Families (Batch Mode)

You don't need a brand-new resume for every single application if they are identical roles. Save generic profiles and generate them in batch:

```bash
mkdir -p data/karine_justino/job_profiles
# Create a .txt file per family, e.g. data/karine_justino/job_profiles/data_scientist.txt

make list-roles
make role ROLE=data_scientist
make all-roles

```

---

## 6. Repository Structure

```
.
├── README.md                      # You are here
├── main.py                        # CLI Entry Point
├── Makefile                       # Command shortcuts
├── src/                           # Core logic, LLM factory, scripts
├── prompts/                       # Agent system prompts
├── resume/                        # LaTeX and PDF generation logic
├── tools/                         # CrewAI tools
├── examples/                      # Fictional sample data (safe for git)
├── tests/                         # Unit tests
└── .env.example                   # Environment configuration

```

---

## 7. Contributing & License

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details. PRs for new resume templates, improved ATS prompts, or bug fixes are highly welcome. **Never include real personal data in PRs or Issues.**

License: MIT.

---

## 8. About the Author

**Karine Duarte Justino de Almeida** is a Data Scientist and AI Alignment Specialist based in São Paulo, Brazil. With a unique background blending Clinical Neuropsychology with heavy data engineering (PyTorch, PySpark, LangChain), this framework was born out of a desire to treat the job search as an actionable, programmatic, and bias-free ETL pipeline.

* **Email:** karineduartejustino@proton.me
* **LinkedIn:** [Karine Justino](https://www.linkedin.com/in/karinedjustino/)
* **GitHub:** [krinedrtjst](https://github.com/krinedrtjst)

```

```