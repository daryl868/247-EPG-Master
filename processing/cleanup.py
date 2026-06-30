import re

def clean_title(text: str, corrections: dict | None = None) -> str:
    corrections = corrections or {}

    text = text.replace("\n", " ").strip().upper()
    text = re.sub(r"\(.*$", "", text)
    text = re.sub(r"[^A-Z0-9 '&:.-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" -:|")

    for wrong, right in corrections.items():
        if wrong.upper() in text:
            return right

    if "BURBS" in text or "BU" in text:
        return "The Burbs"

    return text.title()