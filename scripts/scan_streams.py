#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import json
import subprocess
import tempfile
import sys

from PIL import Image, ImageOps, ImageFilter
import pytesseract

from clean_titles import split_title_subtitle

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def crop_box(img, profile):
    w, h = img.size
    c = profile["crop"]
    x1 = int(c["x"] * w)
    y1 = int(c["y"] * h)
    x2 = x1 + int(c["w"] * w)
    y2 = y1 + int(c["h"] * h)
    return img.crop((x1, y1, x2, y2))

def preprocess(img, threshold, scale=2):
    if scale and scale > 1:
        img = img.resize((img.width * scale, img.height * scale))
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda p: 255 if p > threshold else 0)
    return img

def capture(url, path, seconds):
    cmd = ["ffmpeg", "-y", "-ss", str(seconds), "-i", url, "-frames:v", "1", "-q:v", "2", str(path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=True)

def ocr_image(img, profile):
    psm = profile.get("psm", 6)
    data = pytesseract.image_to_data(img, config=f"--psm {psm}", output_type=pytesseract.Output.DICT)
    words = []
    confs = []
    for text, conf in zip(data.get("text", []), data.get("conf", [])):
        text = text.strip()
        try:
            conf = float(conf)
        except Exception:
            conf = -1
        if text and conf >= 0:
            words.append(text)
            confs.append(conf)
    return " ".join(words), (sum(confs) / len(confs) if confs else 0)

def scan_channel(channel, profile, settings, corrections):
    frames = int(settings["ocr"].get("frames_per_stream", 5))
    interval = int(settings["ocr"].get("frame_interval_seconds", 8))
    best_text, best_conf = "", 0

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for idx in range(frames):
            frame = td / f"frame_{idx}.jpg"
            try:
                capture(channel["stream_url"], frame, idx * interval)
                img = Image.open(frame)
                crop = crop_box(img, profile)
                proc = preprocess(crop, int(profile.get("threshold", 165)), int(profile.get("scale", 2)))
                debug_name = channel["id"].replace(".", "_")
                (ROOT / "cache/crops").mkdir(parents=True, exist_ok=True)
                proc.save(ROOT / "cache/crops" / f"{debug_name}_{idx}.png")
                text, conf = ocr_image(proc, profile)
                if conf > best_conf:
                    best_text, best_conf = text, conf
            except Exception as e:
                channel["last_ocr_error"] = str(e)

    title, subtitle = split_title_subtitle(best_text, corrections)
    return title, subtitle, best_text, best_conf

def main(provider_arg=None):
    settings = load_json(ROOT / "config/settings.json")
    profiles = load_json(ROOT / "config/ocr_profiles.json")
    corrections = load_json(ROOT / "config/title_corrections.json").get("corrections", {})
    index = load_json(ROOT / "config/providers.json")

    provider_paths = [provider_arg] if provider_arg else [p["path"] for p in index["providers"]]
    changed = False

    for provider_path in provider_paths:
        path = ROOT / provider_path
        provider = load_json(path)

        for ch in provider["channels"]:
            if not ch.get("ocr_enabled") or not ch.get("stream_url"):
                continue

            profile = profiles.get(ch.get("ocr_profile", "auto"), profiles["auto"])
            title, subtitle, raw, conf = scan_channel(ch, profile, settings, corrections)

            ch["last_ocr_text"] = raw
            ch["last_ocr_confidence"] = round(conf, 2)

            if conf < float(settings["ocr"].get("minimum_confidence", 55)):
                continue

            if title and title.lower() != str(ch.get("show", "")).lower():
                ch.setdefault("history", []).append({
                    "show": ch.get("show", ""),
                    "subtitle": ch.get("subtitle", ""),
                    "changed_at": datetime.utcnow().isoformat() + "Z"
                })
                ch["show"] = title
                if subtitle:
                    ch["subtitle"] = subtitle
                ch["last_changed"] = datetime.utcnow().isoformat() + "Z"
                changed = True

        save_json(path, provider)

    if changed:
        subprocess.run([sys.executable, str(ROOT / "scripts/build_epg.py")], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
