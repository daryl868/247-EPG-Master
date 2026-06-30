from rapidfuzz import process, fuzz

def match_title(ocr_title, known_titles, min_score=80):
    if not ocr_title or not known_titles:
        return ocr_title, 0

    match = process.extractOne(
        ocr_title,
        known_titles,
        scorer=fuzz.WRatio
    )

    if not match:
        return ocr_title, 0

    title, score, _ = match

    if score >= min_score:
        return title, score

    return ocr_title, score
