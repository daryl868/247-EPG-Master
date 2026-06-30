import pytesseract
from PIL import Image

def ocr_with_tesseract(image: Image.Image, psm: int = 7) -> tuple[str, float]:
    config = f"--psm {psm} " + '-c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:,\'.-() &"'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
    words, confs = [], []
    for text, conf in zip(data.get("text", []), data.get("conf", [])):
        text = str(text).strip()
        try:
            conf = float(conf)
        except Exception:
            conf = -1
        if text and conf >= 0:
            words.append(text)
            confs.append(conf)
    return " ".join(words).strip(), round(sum(confs) / len(confs), 2) if confs else 0.0
