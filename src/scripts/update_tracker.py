import csv
import logging
import re
from datetime import datetime
from pathlib import Path

# Configure logger if not already configured globally
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def log_application(person: str, role: str, output_dir: str) -> None:
    """
    Logs the generated job application to a CSV tracker, 
    extracting the FIT_SCORE from the rating report if available.
    """
    tracker_path = Path(f"data/{person}/tracker.csv")
    report_path = Path(output_dir) / "rating_report.md"
    
    fit_score = "N/A"
    
    # 1. Safely extract the Fit Score using robust regex
    if report_path.is_file():
        try:
            content = report_path.read_text(encoding="utf-8")
            # Handles "FIT_SCORE: 85", "FIT_SCORE - 8.5", "fit_score 90", etc.
            match = re.search(r"FIT_SCORE\s*[:\-]?\s*(\d{1,3}(?:\.\d+)?)", content, re.IGNORECASE)
            if match:
                fit_score = match.group(1)
        except Exception as e:
            logger.warning(f"Could not read fit score from {report_path.name}: {e}")

    # 2. Ensure the output directory exists
    tracker_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = tracker_path.is_file()
    
    # 3. Safely append to the CSV
    try:
        with tracker_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if it's a brand new file
            if not file_exists:
                writer.writerow(["Date", "Person", "Role", "Fit_Score", "Status"])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d"), 
                person, 
                role, 
                fit_score, 
                "Generated"
            ])
            
        logger.info(f"Application logged to {tracker_path} with Fit Score: {fit_score}")
        
    except PermissionError:
        logger.error(f"Permission denied: Please close '{tracker_path.name}' if it is open in Excel.")
    except Exception as e:
        logger.error(f"Failed to log application to tracker: {e}")