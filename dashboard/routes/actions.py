from flask import Blueprint, redirect, url_for
from services.system_service import run_cmd

actions_bp = Blueprint("actions", __name__)

PYTHON = "/EPG_Vision_Studio_v1/venv/bin/python"

@actions_bp.route("/run-update")
def run_update():
    run_cmd([PYTHON, "scripts/run_and_publish.py"])
    return redirect(url_for("dashboard.home"))

@actions_bp.route("/validate")
def validate():
    run_cmd([PYTHON, "scripts/validate_xml.py"])
    return redirect(url_for("dashboard.home"))
