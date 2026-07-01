import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CACHE_DIR = ROOT / "data" / "metadata"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_file(title):
    safe = (
        title.lower()
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
        .replace("?", "")
        .replace("*", "")
    )
    return CACHE_DIR / f"{safe}.json"


def load(title):
    f = cache_file(title)

    if not f.exists():
        return None

    return json.loads(f.read_text(encoding="utf-8"))


def save(title, data):
    f = cache_file(title)

    f.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
