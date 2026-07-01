from flask import Blueprint, redirect, url_for
from pathlib import Path
import subprocess
from datetime import datetime

actions_bp = Blueprint("actions", __name__)

ROOT = Path(__file__).resolve().parents[2]
PYTHON = "/EPG_Vision_Studio_v1/venv/bin/python"
ACTION_LOG = Path("/var/log/epg_dashboard_actions.log")

def run_and_log(name, cmd):
    ACTION_LOG.parent.mkdir(parents=True, exist_ok=True)

    with ACTION_LOG.open("a", encoding="utf-8") as log:
        log.write("\n" + "=" * 80 + "\n")
        log.write(f"{datetime.utcnow().isoformat()}Z - {name}\n")
        log.write("=" * 80 + "\n")

        result = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True
        )

        log.write(result.stdout)
        log.write(result.stderr)
        log.write(f"\nExit Code: {result.returncode}\n")

    return result.returncode

@actions_bp.route("/run-update")
def run_update():
    run_and_log(
        "Run OCR / Build / Publish",
        [PYTHON, "scripts/run_and_publish.py"]
    )
    return redirect(url_for("logs.logs"))

@actions_bp.route("/validate")
def validate():
    run_and_log(
        "Validate XML",
        [PYTHON, "scripts/validate_xml.py"]
    )
    return redirect(url_for("logs.logs"))
