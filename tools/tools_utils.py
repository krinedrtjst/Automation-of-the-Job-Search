import difflib
import logging
import argparse
from pathlib import Path
from typing import Tuple

import fitz  # PyMuPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).

    Args:
        pdf_file (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    text = ""
    try:
        # Using context manager ensures the document is properly closed
        with fitz.open(pdf_file) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_file}: {e}")
        raise
    return text


def compare_texts(text1: str, text2: str) -> str:
    """
    Compares two texts and generates an HTML diff.

    Args:
        text1 (str): The first text to compare.
        text2 (str): The second text to compare.

    Returns:
        str: HTML representation of the differences between the two texts.
    """
    d = difflib.HtmlDiff()
    return d.make_file(text1.splitlines(), text2.splitlines())


def generate_comparison_pdf(pdf_file1: str, pdf_file2: str, output_pdf: str) -> None:
    """
    Generates a PDF file containing a line-by-line comparison of two PDF files.
    Uses a monospaced font so the diff aligns correctly.

    Args:
        pdf_file1 (str): The path to the original PDF file.
        pdf_file2 (str): The path to the modified PDF file.
        output_pdf (str): The path where the comparison PDF will be saved.
    """
    text1 = extract_text_from_pdf(pdf_file1)
    text2 = extract_text_from_pdf(pdf_file2)

    # Create a new PDF to write the comparison
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 1 * inch  # Fixed syntax error here

    diff = difflib.ndiff(text1.splitlines(), text2.splitlines())
    
    # Start from the top of the page
    y_position = height - margin  

    # Use a monospaced font for diffs so indentation and characters align
    c.setFont("Courier", 9)
    line_height = 11

    # Loop through the diff and add text with color coding
    for line in diff:
        # Clean up the line and truncate to prevent it from running off the page edge
        # 85 characters roughly fit within the letter page margins at Courier 9pt
        safe_line = line[:85].replace('\t', '    ')

        if line.startswith('-'):
            c.setFillColor(colors.red)
        elif line.startswith('+'):
            c.setFillColor(colors.green)
        elif line.startswith('?'):
            # Skip the '?' indicator lines from ndiff for a cleaner PDF output
            continue
        else:
            c.setFillColor(colors.black)

        # Write the line to the PDF (skipping the first two diff characters '- '/'+ ')
        c.drawString(margin, y_position, safe_line[2:] if len(safe_line) > 2 else "")

        # Move down for the next line
        y_position -= line_height
        
        # Check if we need a new page
        if y_position < margin:
            c.showPage()
            c.setFont("Courier", 9)
            y_position = height - margin

    c.save()
    logger.info(f"Comparison PDF successfully generated at: {output_pdf}")


def count_pages_and_lines(pdf_path: str) -> Tuple[int, int]:
    """
    Counts the number of pages and non-empty lines on the last page of a PDF.
    Refactored to use PyMuPDF (fitz) instead of PyPDF2 for better speed and accuracy.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        tuple: (number of pages, count of non-empty lines on the last page).
    """
    try:
        with fitz.open(pdf_path) as doc:
            num_pages = len(doc)
            
            if num_pages == 0:
                return 0, 0
                
            last_page = doc[num_pages - 1]
            text = last_page.get_text()
            
            # Count non-empty lines
            lines = [line for line in text.split('\n') if line.strip()]
            line_count = len(lines)
            
            return num_pages, line_count
            
    except Exception as e:
        logger.error(f"Failed to count pages for {pdf_path}: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Utility Tools: Count pages and lines of a PDF.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    
    args = parser.parse_args()
    
    target_pdf = Path(args.pdf_path)
    if not target_pdf.exists():
        logger.error(f"File not found: {target_pdf}")
        exit(1)
        
    pages, lines = count_pages_and_lines(str(target_pdf))
    logger.info(f"Total pages: {pages} | Lines on last page: {lines}")