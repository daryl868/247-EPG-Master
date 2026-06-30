import re

NOISE_PATTERNS = [
    r"\bHD\b", r"ᴴᴰ", r"\bNEW\b", r"\bLIVE\b", r"\bNOW PLAYING\b",
    r"\bNetflix Series \d+\b", r"\bPeacock Original \d+\b",
    r"\bHulu Originals \d+\b", r"\bPrime Video \d+\b",
    r"\bSky Store Premiere \d+\b", r"\bApple TV\+ Series \d+\b"
]

def normalize_spacing(text):
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()

def apply_corrections(text, corrections):
    for wrong, right in corrections.items():
        text = re.sub(re.escape(wrong), right, text, flags=re.I)
    return text

def clean_title(text, corrections=None):
    text = normalize_spacing(text)
    corrections = corrections or {}
    text = apply_corrections(text, corrections)
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.I)
    text = normalize_spacing(text)
    text = text.strip(" -:|>")
    return text

def split_title_subtitle(text, corrections=None):
    text = clean_title(text, corrections)

    m = re.search(r"\bS(\d{1,2})\b(?:\s*\(?Serie\)?)?\s*\((\d{4})\)", text, flags=re.I)
    if m:
        title = text[:m.start()].strip(" -:")
        return title, f"Season {int(m.group(1))} ({m.group(2)})"

    m = re.search(r"Season\s+0?(\d{1,2}).*?\((\d{4})\)", text, flags=re.I)
    if m:
        title = text[:m.start()].strip(" -:")
        return title, f"Season {int(m.group(1))} ({m.group(2)})"

    m = re.search(r"\((\d{4})\)", text)
    if m:
        title = text[:m.start()].strip(" -:")
        return title, f"Movie ({m.group(1)})"

    return text, ""
