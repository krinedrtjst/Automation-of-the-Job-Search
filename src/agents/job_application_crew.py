import json
import logging
import os
import sys
from pathlib import Path
from textwrap import dedent

from crewai import Agent, Crew, Process, Task

current_dir = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

# Assuming these tools exist in your tools/resume_tools.py
from tools.resume_tools import (
    generate_resume_tool,
    save_resume_json,
)
from resume.generator import generate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class JobApplicationCrew:
    def __init__(
        self,
        role: str = None,
        job_profile_path: str = "data/dev_procurando/job_desc.txt",
        output_dir: str = "outputs",
        provider: str = None,
        language: str = "pt-BR",
        original_resume_path: str = "data/dev_procurando/resume.json",
    ):
        self.role = role
        self.job_profile_path = job_profile_path
        self.output_dir = output_dir
        self.provider = provider
        self.language = language
        self.original_resume_path = original_resume_path

        os.environ["RESUME_OUTPUT_DIR"] = output_dir
        os.environ["RESUME_LANGUAGE"] = language

        # Ensure output directories exist
        Path(self.output_dir, "json").mkdir(parents=True, exist_ok=True)
        Path(self.output_dir, "latex").mkdir(parents=True, exist_ok=True)
        Path(self.output_dir, "pdf").mkdir(parents=True, exist_ok=True)

        with open(job_profile_path, "r", encoding="utf-8") as f:
            self.job_description = f.read()

        with open(original_resume_path, "r", encoding="utf-8") as f:
            self.original_resume = json.load(f)

        # Load only this person's supporting sources. Keep the canonical JSON untouched.
        person = Path(original_resume_path).parent.name
        self.source_context = ""
        for filename in ("profile_truth.md", "about_me.md", "vagas_excluidas.md"):
            source = Path("input") / person / filename
            if source.exists():
                self.source_context += f"\n### {filename}\n{source.read_text(encoding='utf-8')}\n"
        
        # KARINE'S STRICT PROFILE CONSTRAINTS INJECTED INTO SYSTEM CONTEXT
        self.source_context = (
            "\nCRITICAL SOURCE RULES & ZERO-HALLUCINATION POLICY:\n"
            "1. profile_truth.md is the ABSOLUTE source of truth. It overrides the base JSON.\n"
            "2. METRIC INTEGRITY: You MUST preserve the exact metrics: 15TB+ multimodal datasets, "
            "99.2% accuracy, and 40% bias reduction. Do not alter or inflate them.\n"
            "3. ANTI-HALLUCINATION: NEVER invent skills. Specifically, NEVER add React, Node.js, "
            "Full-Stack Web Development, or AWS/GCP Cloud Architecture from scratch.\n"
            "4. INTERDISCIPLINARY VALUE: Always elegantly bridge the candidate's Clinical Neuropsychology "
            "background with their rigorous AI Data Science / Alignment tech stack.\n"
            "5. Ignore placeholders and unconfirmed credentials. ALWAYS include every academic degree.\n"
            + self.source_context
        )

        generated_resume_path = Path(output_dir, "json", "resume.json")
        if generated_resume_path.exists():
            with open(generated_resume_path, "r", encoding="utf-8") as f:
                self.resume_generated = json.load(f)
        else:
            self.resume_generated = self.original_resume

        self.llm = self._get_llm()

    def _get_llm(self):
        try:
            from src.llm_factory import get_llm
            return get_llm(provider=self.provider)
        except ImportError:
            logger.warning("llm_factory not found, defaulting to CrewAI's default LLM.")
            return None

    @property
    def _resume_path(self) -> Path:
        return Path(self.output_dir, "json", "resume.json")

    def _kickoff(self, agents, tasks):
        crew = Crew(agents=agents, tasks=tasks, verbose=True, process=Process.sequential)
        result = crew.kickoff()
        logger.info(f"Token Usage: {crew.usage_metrics}")
        return result

    def _render(self):
        logger.info("Rendering PDF via LaTeX...")
        generate(
            json_path=str(self._resume_path),
            latex_path=os.path.join(self.output_dir, "latex", "output_resume.tex"),
            pdf_dir=os.path.join(self.output_dir, "pdf"),
        )

    def run(self):
        # ---------------------------------------------------------
        # AGENTS (The Command Center tailored for Karine)
        # ---------------------------------------------------------
        llm_kwargs = {"llm": self.llm} if self.llm else {}

        job_matcher = Agent(
            name="Data Science Strategist",
            role="AI Alignment & ML Recruitment Analyst",
            goal="Calculate an objective fit score and map the job's needs to the candidate's PySpark/PyTorch/RLHF stack.",
            backstory="You strictly evaluate whether the candidate meets the employer's hard data engineering and ML requirements. You value statistical rigor over buzzwords.",
            verbose=True, allow_delegation=False, **llm_kwargs
        )

        resume_optimizer = Agent(
            name="Resume Optimizer",
            role="ATS JSON Architect",
            goal="Tailor the resume JSON using ONLY verified facts, triggering save_resume_json.",
            backstory="You are a strict ATS optimization engine. You never hallucinate frontend or devops skills. You prioritize AI Safety, ETL pipelines, and the 15TB+ metrics.",
            tools=[generate_resume_tool, save_resume_json],
            verbose=True, allow_delegation=False, **llm_kwargs
        )

        coverage_reviewer = Agent(
            name="Zero-Hallucination Auditor",
            role="Red Team Compliance Auditor",
            goal="Audit the tailored resume JSON against profile_truth.md to catch any hallucinations.",
            backstory="You are a strict Trust & Safety auditor for resumes. If a skill (like React or AWS architecture) appears in the JSON but isn't in profile_truth.md, you flag it immediately as a critical failure.",
            verbose=True, allow_delegation=False, **llm_kwargs
        )

        interview_copilot = Agent(
            name="Interview Copilot",
            role="Senior AI Safety Interviewer",
            goal="Generate a rigorous interview prep guide bridging Clinical Neuropsychology with ML pipelines.",
            backstory="You test causal inference, model evaluation, and RLHF methodologies. You help candidates frame their non-traditional backgrounds as massive strategic advantages.",
            verbose=True, allow_delegation=False, **llm_kwargs
        )

        # ---------------------------------------------------------
        # PROMPT INJECTION UTILITY
        # ---------------------------------------------------------
        def load_prompt(filename: str, **kwargs) -> str:
            prompt_path = Path(grandparent_dir) / "prompts" / filename
            if not prompt_path.exists():
                logger.error(f"PROMPT FILE MISSING: {prompt_path}")
                return f"PROMPT FILE MISSING: {filename}"
            template = prompt_path.read_text(encoding="utf-8")
            return template.format(**kwargs)

        resume_json_str = json.dumps(self.original_resume, ensure_ascii=False, indent=2)

        # ---------------------------------------------------------
        # TASKS (Strict Linear Pipeline)
        # ---------------------------------------------------------
        
        task_match = Task(
            description=load_prompt(
                "job_matcher.md", 
                resume_json=resume_json_str, 
                job_description=self.job_description
            ),
            agent=job_matcher,
            expected_output="A gap analysis markdown report ending with FIT_SCORE: <number>"
        )

        task_optimize = Task(
            description=load_prompt(
                "resume_optimizer.md",
                resume_json=resume_json_str,
                job_description=self.job_description,
                source_context=self.source_context
            ),
            agent=resume_optimizer,
            expected_output="A valid JSON object representing the tailored resume. MUST use the save_resume_json tool.",
            context=[task_match]
        )

        task_audit = Task(
            description=load_prompt(
                "coverage_reviewer.md",
                resume_json=resume_json_str,
                job_description=self.job_description
            ) + "\n\nTAILORED RESUME CONTEXT TO AUDIT:\n{task_optimize.output}\n" + self.source_context,
            agent=coverage_reviewer,
            expected_output="A coverage review markdown document explicitly listing gaps, strong coverage, and flagging any hallucinations.",
            context=[task_optimize]
        )

        task_interview = Task(
            description=load_prompt(
                "interview_copilot.md",
                resume_json=resume_json_str,
                job_description=self.job_description
            ) + "\n\nIDENTIFIED GAPS & AUDIT:\n{task_audit.output}",
            agent=interview_copilot,
            expected_output="A comprehensive interview prep guide featuring STAR method answers.",
            context=[task_audit]
        )

        # ---------------------------------------------------------
        # EXECUTION (Straight line, no loops)
        # ---------------------------------------------------------
        logger.info(f"Starting Job Application Crew for role: {self.role or 'Default'}")
        
        result = self._kickoff(
            [job_matcher, resume_optimizer, coverage_reviewer, interview_copilot],
            [task_match, task_optimize, task_audit, task_interview]
        )

        # 1. Render the final PDF based on whatever Agent 2 saved
        self._render()

        # 2. Save the outputs to the outputs folder
        Path(self.output_dir, "rating_report.md").write_text(task_match.output.raw, encoding="utf-8")
        Path(self.output_dir, "coverage_review.md").write_text(task_audit.output.raw, encoding="utf-8")
        Path(self.output_dir, "interview_prep.md").write_text(task_interview.output.raw, encoding="utf-8")

        role_label = f" [{self.role}]" if self.role else ""
        logger.info(f"Outputs{role_label} saved successfully to: {self.output_dir}/")

        return result

def main():
    job_application_crew = JobApplicationCrew()
    final_result = job_application_crew.run()
    logger.info("Pipeline execution completed.")

if __name__ == "__main__":
    main()