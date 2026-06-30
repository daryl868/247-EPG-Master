#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import json
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocr.engine import test_channel
from processing.matcher import match_title

provider_arg = sys.argv[1] if len(sys.argv) > 1 else "providers/peacock.json"
provider_path = ROOT / provider_arg

provider = json.loads(provider_path.read_text(encoding="utf-8"))

# Load global title database

titles_file = ROOT / "config" / "global_titles.json"

if not titles_file.exists():
    raise FileNotFoundError(
        "config/global_titles.json not found"
    )

known_titles = json.loads(
    titles_file.read_text(encoding="utf-8")
)["titles"]

print(f"Loaded {len(known_titles)} known titles.")
changes = 0

print(f"\nScanning provider: {provider['label']}")
print("=" * 60)

for idx, channel in enumerate(provider["channels"]):

    if not channel.get("ocr_enabled", False):
        print(f"Skipping {channel['name']} (OCR disabled)")
        continue

    print(f"\n[{idx+1}/{len(provider['channels'])}] {channel['name']}")

    try:
        result = test_channel(provider_arg, idx)
        best = result["best"]

        raw_title = best.get("raw", "").strip()
        clean_title = best.get("clean", "").strip()
        confidence = best.get("confidence", 0)

        matched_title, match_score = match_title(clean_title, known_titles)

        print(f" OCR Raw      : {raw_title}")
        print(f" OCR Clean    : {clean_title}")
        print(f" Match        : {matched_title}")
        print(f" Match Score  : {match_score}")
        print(f" OCR Conf     : {confidence}")

        channel["last_ocr_text"] = raw_title
        channel["last_ocr_confidence"] = confidence

        # Require BOTH OCR confidence AND fuzzy match confidence
        if confidence < 35:
            print(" Skipped (low OCR confidence)")
            continue

        if match_score < 85:
            print(" Skipped (poor fuzzy match)")
            continue

        old = channel.get("show", "")

        if old != matched_title:

            channel.setdefault("history", []).append({
                "old": old,
                "new": matched_title,
                "changed_at": datetime.utcnow().isoformat() + "Z"
            })

            channel["show"] = matched_title
            channel["last_changed"] = datetime.utcnow().isoformat() + "Z"

            changes += 1

            print(f" Updated: {old} -> {matched_title}")

        else:
            print(" No change")

    except Exception as ex:
        print(f" ERROR: {ex}")

provider_path.write_text(
    json.dumps(provider, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("\n")
print("=" * 60)
print(f"Finished. {changes} channel(s) updated.")
print("Rebuilding XML...")
print("=" * 60)

subprocess.run(
    [sys.executable, str(ROOT / "scripts/build_epg.py")],
    check=True
)
