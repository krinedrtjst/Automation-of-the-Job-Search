# Mid-Life Agent — Project Specification (Adapted for Karine Duarte Justino)

## 1. What was requested

Transform the `mid-life-agent` repository into an intelligent career automation agent capable of:

- **Rewriting and repositioning** the user's resume according to specific job profiles, enforcing strict zero-hallucination protocols.
- **Generating N tailored versions** of the resume, one for each target profile, including (but not limited to):
  - Data Scientist (NLP / ML)
  - AI Alignment Specialist / AI Tutor
  - Machine Learning Engineer (Ethics/Fairness)
  - Business Intelligence / Analytics Engineer
- Support for multiple LLM providers: **OpenAI, Gemini, Grok (xAI), and Anthropic (Claude)**.

---

## 2. Repository Analysis Conclusions

### Current State

| Component | Status |
|---|---|
| Agent Framework | CrewAI (multi-agent, sequential) |
| Existing Agents | 3: Hiring Manager, Resume Editor, Job Applicant |
| Input | `data/resume.json` + `data/job_desc.txt` |
| Output | JSON → LaTeX → PDF + comparative diff |
| Refinement | Iterative loop until score ≥ 8.5 |
| Example CV | Cynthia Dwayne (fictional) |

### Identified Gaps

| Gap | Impact |
|---|---|
| No repositioning agent | The Resume Editor only optimizes format; it does not rewrite the career narrative to highlight interdisciplinary strengths. |
| One job per execution | Lacks support for batch generation across multiple target roles. |
| No curated job profiles | Job descriptions must be created manually every time. |
| Hardcoded LLM (OpenAI default) | Lacks abstraction to seamlessly switch providers. |
| CLI without parameters | Does not accept `--role`, `--all`, or `--provider`. |
| Missing real CV / Master Profile | Only the fictional resume exists; needs adaptation to integrate Karine's `profile_truth.md` and zero-hallucination constraints. |

---

## 3. LLMs in the Project

### Active
- **OpenAI `gpt-4o`** — The implicit CrewAI default when no `llm=` is specified in the agents.
- Authenticated via `OPENAI_API_KEY` in `.env`.

### Inactive (commented)
- **Grok** — Code is present but commented out; the `langchain-xai` package is missing from `requirements.txt`.

### Missing
- Anthropic (Claude) — Not configured.
- Google Gemini — Not configured.

---

## 4. Strategy to Achieve the Objective

### 4.1 New Agent: Career Strategist (Zero-Hallucination Enforcer)

Add a **4th agent** focused exclusively on career repositioning and strict constraint adherence:

```text
Agent: Career Strategist
Responsibilities:
  - Analyze the target job profile.
  - Identify transferable skills from the master profile (`profile_truth.md`), specifically bridging Clinical Neuropsychology with AI Alignment/Safety.
  - Rewrite the "Professional Summary" narrative aligned with the role.
  - Select and prioritize the most relevant experiences (e.g., highlighting 15TB+ data, PySpark, PyTorch, and RLHF).
  - Enforce the Zero-Hallucination Blocklist (e.g., stripping out any generated references to Full-Stack, React, or AWS Cloud Architecture).