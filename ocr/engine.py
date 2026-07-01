from pathlib import Path
from PIL import Image
import json
import shutil
from datetime import datetime

from capture.ffmpeg import capture_frame
from ocr.preprocess import crop_image, preprocess_for_ocr
from ocr.tesseract_engine import ocr_with_tesseract
from processing.cleanup import clean_title

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def choose_best_ocr_result(results):
    if not results:
        return {}

    grouped = {}

    for result in results:
        clean = result.get("clean", "").strip()
        conf = float(result.get("confidence", 0))

        if not clean:
            continue

        if clean not in grouped:
            grouped[clean] = {
                "clean": clean,
                "count": 0,
                "total_confidence": 0,
                "best": result
            }

        grouped[clean]["count"] += 1
        grouped[clean]["total_confidence"] += conf

        if conf > grouped[clean]["best"].get("confidence", 0):
            grouped[clean]["best"] = result

    if not grouped:
        return max(results, key=lambda r: r.get("confidence", 0))

    winner = max(
        grouped.values(),
        key=lambda x: (
            x["count"],
            x["total_confidence"] / x["count"]
        )
    )

    best = winner["best"]
    best["vote_count"] = winner["count"]
    best["vote_avg_confidence"] = round(
        winner["total_confidence"] / winner["count"],
        2
    )

    return best

def safe_name(text):
    return (
        text.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
        .replace(".", "_")
    )

def test_channel(provider_path: str, channel_index: int = 0) -> dict:
    settings = load_json(ROOT / "config/settings.json")
    profiles = load_json(ROOT / "config/ocr_profiles.json")
    corrections = load_json(ROOT / "config/title_corrections.json").get("corrections", {})

    provider = load_json(ROOT / provider_path)
    channel = provider["channels"][channel_index]

    profile = profiles[channel.get("ocr_profile", "default_top_left")]
    frame_seconds = settings["ocr"].get("frame_seconds", [5, 15, 25])

    results = []

    provider_slug = safe_name(provider.get("label", "provider"))
    channel_slug = safe_name(channel.get("id", channel.get("name", "channel")))
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    debug_dir = ROOT / "debug" / provider_slug
    debug_dir.mkdir(parents=True, exist_ok=True)

    screenshot_dir = ROOT / "data" / "screenshots" / provider_slug
    crop_dir = ROOT / "data" / "crops" / provider_slug

    screenshot_dir.mkdir(parents=True, exist_ok=True)
    crop_dir.mkdir(parents=True, exist_ok=True)

    for idx, second in enumerate(frame_seconds, start=1):
        frame_path = debug_dir / f"{channel_slug}_frame_{idx}.png"
        crop_path = debug_dir / f"{channel_slug}_crop_{idx}.png"

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

        archived_frame = screenshot_dir / f"{channel_slug}_{timestamp}_frame_{idx}.png"
        archived_crop = crop_dir / f"{channel_slug}_{timestamp}_crop_{idx}.png"

        shutil.copy2(frame_path, archived_frame)
        shutil.copy2(crop_path, archived_crop)

        results.append({
            "frame": idx,
            "second": second,
            "raw": raw,
            "clean": clean,
            "confidence": conf,
            "crop": str(crop_path.relative_to(ROOT)),
            "frame_path": str(frame_path.relative_to(ROOT)),
            "archived_frame": str(archived_frame.relative_to(ROOT)),
            "archived_crop": str(archived_crop.relative_to(ROOT))
        })

    best = choose_best_ocr_result(results)

    return {
        "channel": channel["name"],
        "expected": channel.get("show", ""),
        "best": best,
        "results": results
    }
