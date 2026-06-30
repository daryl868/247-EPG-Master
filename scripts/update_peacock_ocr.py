#!/usr/bin/env python3
from pathlib import Path
import sys, json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocr.engine import test_channel

provider_path = ROOT / "providers/peacock.json"
data = json.loads(provider_path.read_text(encoding="utf-8"))

result = test_channel("providers/peacock.json", 0)
best = result["best"]
new_title = best.get("clean", "")
confidence = best.get("confidence", 0)

channel = data["channels"][0]

if new_title and confidence >= 40:
    old_title = channel.get("show", "")

    channel["last_ocr_text"] = best.get("raw", "")
    channel["last_ocr_confidence"] = confidence

    if new_title != old_title:
        channel.setdefault("history", []).append({
            "old": old_title,
            "new": new_title,
            "changed_at": datetime.utcnow().isoformat() + "Z"
        })
        channel["show"] = new_title
        channel["last_changed"] = datetime.utcnow().isoformat() + "Z"

    provider_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated Peacock Original 1: {old_title} → {new_title} ({confidence})")
else:
    print(f"Skipped update. OCR result too weak: {new_title} ({confidence})")
