from flask import Blueprint, render_template
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
providers_bp = Blueprint("providers", __name__)
PYTHON = "/EPG_Vision_Studio_v1/venv/bin/python"

def load_provider(file_name):
    path = ROOT / "providers" / file_name
    return json.loads(path.read_text(encoding="utf-8"))

def run_cmd(cmd):
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return result.stdout + result.stderr

@providers_bp.route("/")
def list_providers():
    providers = []

    for path in sorted((ROOT / "providers").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        channels = data.get("channels", [])
        providers.append({
            "file": path.name,
            "label": data.get("label", path.stem),
            "channels": len(channels),
            "ocr_enabled": len([c for c in channels if c.get("ocr_enabled")])
        })

    return render_template("providers.html", providers=providers)

@providers_bp.route("/<file_name>")
def provider_detail(file_name):
    data = load_provider(file_name)
    channels = data.get("channels", [])

    return render_template(
        "provider_detail.html",
        provider=data,
        file_name=file_name,
        channels=channels
    )

@providers_bp.route("/<file_name>/channel/<int:channel_index>")
def channel_detail(file_name, channel_index):
    data = load_provider(file_name)
    channels = data.get("channels", [])

    if channel_index < 0 or channel_index >= len(channels):
        return "Channel not found", 404

    channel = channels[channel_index]

    return render_template(
        "channel_detail.html",
        provider=data,
        file_name=file_name,
        channel=channel,
        channel_index=channel_index
    )

@providers_bp.route("/<file_name>/channel/<int:channel_index>/live-ocr")
def live_ocr(file_name, channel_index):
    output = run_cmd([
        PYTHON,
        "scripts/test_channel_ocr.py",
        f"providers/{file_name}",
        str(channel_index)
    ])

    parsed = None
    try:
        parsed = json.loads(output)
    except Exception:
        parsed = None

    return render_template(
        "live_ocr.html",
        file_name=file_name,
        channel_index=channel_index,
        output=output,
        parsed=parsed
    )
