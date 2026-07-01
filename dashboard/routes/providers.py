from flask import Blueprint, render_template
from pathlib import Path
import json
import subprocess

from services.db_service import latest_channel_result, channel_ocr_history

ROOT = Path(__file__).resolve().parents[2]
providers_bp = Blueprint("providers", __name__)
PYTHON = "/EPG_Vision_Studio_v1/venv/bin/python"


def load_provider(file_name):
    path = ROOT / "providers" / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    return result.stdout + result.stderr


def provider_list():
    providers = []

    for path in sorted((ROOT / "providers").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            channels = data.get("channels", [])

            providers.append({
                "file": path.name,
                "label": data.get("label", path.stem),
                "channels": len(channels),
                "ocr_enabled": len([c for c in channels if c.get("ocr_enabled")]),
                "status": "Online"
            })

        except Exception as ex:
            providers.append({
                "file": path.name,
                "label": path.stem,
                "channels": 0,
                "ocr_enabled": 0,
                "status": f"Error: {ex}"
            })

    return providers


@providers_bp.route("/")
def list_providers():
    return render_template(
        "providers.html",
        providers=provider_list()
    )


@providers_bp.route("/<file_name>")
def provider_detail(file_name):
    data = load_provider(file_name)
    channels = data.get("channels", [])

    enriched_channels = []

    for idx, channel in enumerate(channels):
        latest = latest_channel_result(f"providers/{file_name}", idx)

        enriched_channels.append({
            "index": idx,
            "name": channel.get("name", ""),
            "id": channel.get("id", ""),
            "show": channel.get("show", ""),
            "subtitle": channel.get("subtitle", ""),
            "ocr_enabled": channel.get("ocr_enabled", False),
            "ocr_profile": channel.get("ocr_profile", ""),
            "latest_ocr": latest
        })

    return render_template(
        "provider_detail.html",
        provider=data,
        file_name=file_name,
        channels=enriched_channels
    )


@providers_bp.route("/<file_name>/channel/<int:channel_index>")
def channel_detail(file_name, channel_index):
    data = load_provider(file_name)
    channels = data.get("channels", [])

    if channel_index < 0 or channel_index >= len(channels):
        return "Channel not found", 404

    channel = channels[channel_index]
    provider_key = f"providers/{file_name}"

    latest_ocr = latest_channel_result(provider_key, channel_index)
    ocr_history = channel_ocr_history(provider_key, channel_index, 25)

    return render_template(
        "channel_detail.html",
        provider=data,
        file_name=file_name,
        channel=channel,
        channel_index=channel_index,
        latest_ocr=latest_ocr,
        ocr_history=ocr_history
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
