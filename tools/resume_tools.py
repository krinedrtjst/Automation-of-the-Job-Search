import json
import logging
import os
import sys
from pathlib import Path
from typing import Union, Dict, Any

from crewai.tools import tool

# Ensure project root is in the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from resume.generator import generate
from tools.tools_utils import count_pages_and_lines, generate_comparison_pdf

logger = logging.getLogger(__name__)


def _output_dir() -> Path:
    """Helper to consistently fetch and resolve the output directory."""
    return Path(os.getenv("RESUME_OUTPUT_DIR", "outputs"))


@tool("save_resume_json")
def save_resume_json(resume_data: Union[str, Dict[str, Any]]) -> str:
    """
    Saves the provided resume data as JSON to the current profile's output directory.

    Args:
        resume_data (Union[str, dict]): A JSON string or Python dict with resume data.

    Returns:
        str: Success or error message.
    """
    try:
        if isinstance(resume_data, str):
            resume_json = json.loads(resume_data)
        elif isinstance(resume_data, dict):
            resume_json = resume_data
        else:
            return "Error: Input must be a JSON string or a Python dictionary."

        json_path = _output_dir() / "json" / "resume.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(resume_json, f, indent=2, ensure_ascii=False)
            
        return f"Resume JSON successfully saved to '{json_path}'."
        
    except json.JSONDecodeError:
        return "Error: The provided string data is not valid JSON."
    except IOError as e:
        return f"Error: Unable to write file. {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"


@tool("generate_resume")
def generate_resume_tool(resume_content: str = "") -> str:
    """
    Generates a LaTeX document from the saved resume JSON and converts it to PDF.

    Args:
        resume_content (str): Ignored — reads from the saved JSON in the output directory.

    Returns:
        str: Confirmation message.
    """
    output_dir = _output_dir()
    json_path = output_dir / "json" / "resume.json"
    latex_path = output_dir / "latex" / "output_resume.tex"
    pdf_dir = output_dir / "pdf"

    # Ensure directories exist
    latex_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    try:
        generate(
            json_path=str(json_path), 
            latex_path=str(latex_path), 
            pdf_dir=str(pdf_dir)
        )
    except Exception as e:
        logger.error(f"LaTeX generation failed: {e}")
        return f"Error generating PDF: {e}"

    pdf_path = pdf_dir / "output_resume.pdf"

    try:
        pages, _ = count_pages_and_lines(str(pdf_path))
        page_feedback = f"Page count: {pages}. Informational only; preserve all distinct professional evidence."
    except Exception:
        page_feedback = "Page count check skipped."

    return f"Resume generated: {pdf_path}. {page_feedback}"


# Prevent CrewAI from caching this function so it generates a fresh PDF every time
generate_resume_tool.cache_function = lambda *_: False


@tool("line count on extra page")
def pgcount_tool(pdf_path: str = "") -> str:
    """
    Counts the number of pages and extra lines on the last page of a PDF.

    Args:
        pdf_path (str): Path to the generated resume PDF file (ignored — always reads the
                        output_resume.pdf from the current output directory).

    Returns:
        str: Page count and line count feedback.
    """
    resolved_path = _output_dir() / "pdf" / "output_resume.pdf"

    if not resolved_path.exists():
        return "PDF not found. Run generate_resume first, then call this tool."

    logger.info(f"Counting pages from: {resolved_path}")
    
    try:
        pages, _ = count_pages_and_lines(str(resolved_path))
        return f"Page count: {pages}. No fixed page limit; review readability and evidence coverage."
    except Exception as e:
        return f"Error checking page count: {str(e)}"


@tool("pdf_comparison_tool")
def pdf_comparison_tool(pdf_file1: str, pdf_file2: str, output_pdf: str) -> str:
    """
    Generates a side-by-side comparison PDF of two resume PDFs.

    Args:
        pdf_file1 (str): Path to the first PDF file.
        pdf_file2 (str): Path to the second PDF file.
        output_pdf (str): Path where the comparison PDF will be saved.

    Returns:
        str: Result message.
    """
    try:
        generate_comparison_pdf(pdf_file1, pdf_file2, output_pdf)
        return f"Comparison PDF successfully generated and saved to {output_pdf}"
    except Exception as e:
        return f"Error generating comparison PDF: {str(e)}"


@tool("save_interview_prep")
def save_interview_prep_tool(content: str) -> str:
    """
    Saves the interview preparation guide as a Markdown file in the output directory.

    Args:
        content (str): The full interview preparation guide in Markdown format.

    Returns:
        str: Success or error message.
    """
    try:
        prep_path = _output_dir() / "interview_prep.md"
        prep_path.parent.mkdir(parents=True, exist_ok=True)
        
        with prep_path.open("w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Interview preparation guide saved to '{prep_path}'."
    except Exception as e:
        return f"Error saving interview prep guide: {str(e)}"