from flask import Blueprint, render_template
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
providers_bp = Blueprint("providers", __name__)

@providers_bp.route("/")
def list_providers():
    providers = []

    for path in sorted((ROOT / "providers").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            channels = data.get("channels", [])
            ocr_enabled = len([c for c in channels if c.get("ocr_enabled")])
            providers.append({
                "file": path.name,
                "label": data.get("label", path.stem),
                "channels": len(channels),
                "ocr_enabled": ocr_enabled
            })
        except Exception as ex:
            providers.append({
                "file": path.name,
                "label": path.stem,
                "channels": 0,
                "ocr_enabled": 0,
                "error": str(ex)
            })

    return render_template("providers.html", providers=providers)
