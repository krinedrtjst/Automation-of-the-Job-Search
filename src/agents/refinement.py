def parse_rating(feedback: str) -> float | None:
    """
    Extracts the final rating from the HR agent's feedback.
    """
    if not feedback:
        return None

    # Bulletproof regex: Finds FINAL_RATING, ignores any non-number characters 
    # (like **, :, -, =, spaces), and captures the first number it hits.
    import re
    pattern = r"FINAL_RATING[^0-9]*([0-9]+(?:[.,][0-9]+)?)"
    
    matches = re.findall(pattern, feedback, re.IGNORECASE)
    
    if not matches:
        return None
        
    try:
        rating_str = matches[-1].replace(",", ".")
        rating = float(rating_str)
        if 1.0 <= rating <= 10.0:
            return rating
        return None
    except ValueError:
        return None