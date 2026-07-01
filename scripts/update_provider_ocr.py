#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import json
import sys
import subprocess

from dashboard.services.db_service import record_ocr_result

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocr.engine import test_channel
from processing.matcher import match_title


provider_arg = sys.argv[1] if len(sys.argv) > 1 else "providers/peacock.json"
provider_path = ROOT / provider_arg

provider = json.loads(provider_path.read_text(encoding="utf-8"))

titles_file = ROOT / "config" / "global_titles.json"

if not titles_file.exists():
    raise FileNotFoundError("config/global_titles.json not found")

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

    print(f"\n[{idx + 1}/{len(provider['channels'])}] {channel['name']}")

    try:
        result = test_channel(provider_arg, idx)
        best = result.get("best", {})

        raw_title = best.get("raw", "").strip()
        clean_title = best.get("clean", "").strip()
        confidence = float(best.get("confidence", 0))

        matched_title, match_score = match_title(clean_title, known_titles)

        vote_count = int(best.get("vote_count", 1))
        vote_avg = float(best.get("vote_avg_confidence", confidence))

        print(f" OCR Raw       : {raw_title}")
        print(f" OCR Clean     : {clean_title}")
        print(f" Match         : {matched_title}")
        print(f" Match Score   : {match_score}")
        print(f" OCR Conf      : {confidence}")
        print(f" Vote Count    : {vote_count}")
        print(f" Vote Avg Conf : {vote_avg}")

        channel["last_ocr_text"] = raw_title
        channel["last_ocr_confidence"] = confidence
        channel["last_ocr_clean"] = clean_title
        channel["last_ocr_match"] = matched_title
        channel["last_ocr_match_score"] = match_score
        channel["last_ocr_vote_count"] = vote_count
        channel["last_ocr_vote_avg_confidence"] = vote_avg

        score = 0

        if confidence >= 80:
            score += 30
        elif confidence >= 50:
            score += 20
        elif confidence >= 35:
            score += 10

        if match_score >= 95:
            score += 40
        elif match_score >= 85:
            score += 25
        elif match_score >= 75:
            score += 10

        if vote_count >= 2:
            score += 20

        if vote_avg >= 75:
            score += 10

        print(f" Decision Score: {score}")

        if score >= 70:
            print(" Decision      : ACCEPT")

        elif score >= 50:
            print(" Decision      : VERIFY WITH TMDB")

            try:
                from metadata.service import MetadataService

                metadata = MetadataService()
                tmdb_result = metadata.lookup(clean_title)

                if tmdb_result and tmdb_result.get("title"):
                    matched_title = tmdb_result["title"]
                    print(f" TMDB Verified : {matched_title}")
                else:
                    print(" Skipped (TMDB could not verify)")
                    continue

            except Exception as ex:
                print(f" Skipped (TMDB verification failed: {ex})")
                continue

        else:
            print(" Decision      : REJECT")
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

            print(f" Updated       : {old} -> {matched_title}")

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
