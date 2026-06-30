from pathlib import Path
from PIL import Image
import json

from capture.ffmpeg import capture_frame
from ocr.preprocess import crop_image, preprocess_for_ocr
from ocr.tesseract_engine import ocr_with_tesseract
from processing.cleanup import clean_title

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_channel(provider_path: str, channel_index: int = 0) -> dict:
    settings = load_json(ROOT / "config/settings.json")
    profiles = load_json(ROOT / "config/ocr_profiles.json")
    corrections = load_json(ROOT / "config/title_corrections.json").get("corrections", {})

    provider = load_json(ROOT / provider_path)
    channel = provider["channels"][channel_index]

    profile = profiles[channel.get("ocr_profile", "default_top_left")]
    frame_seconds = settings["ocr"].get("frame_seconds", [5, 15, 25])

    results = []
    debug_dir = ROOT / "debug" / provider.get("label", "provider").replace(" ", "_").lower()
    debug_dir.mkdir(parents=True, exist_ok=True)

    for idx, second in enumerate(frame_seconds, start=1):
        frame_path = debug_dir / f"{channel['id'].replace('.', '_')}_frame_{idx}.png"
        crop_path = debug_dir / f"{channel['id'].replace('.', '_')}_crop_{idx}.png"

        capture_frame(channel["stream_url"], frame_path, second=second)

        img = Image.open(frame_path)

        cropped = crop_image(
            img,
            profile["crop"],
            profile.get("normalized", False)
        )

        processed = preprocess_for_ocr(
            cropped,
            profile.get("upscale", 4),
            profile.get("threshold", 160)
        )

        processed.save(crop_path)

        raw, conf = ocr_with_tesseract(processed, profile.get("psm", 7))
        clean = clean_title(raw, corrections)

        results.append({
            "frame": idx,
            "second": second,
            "raw": raw,
            "clean": clean,
            "confidence": conf,
            "crop": str(crop_path)
        })

    best = max(results, key=lambda r: r["confidence"]) if results else {}

    return {
        "channel": channel["name"],
        "expected": channel.get("show", ""),
        "best": best,
        "results": results
    }
