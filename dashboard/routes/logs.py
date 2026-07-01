from flask import Blueprint, render_template
from pathlib import Path
from services.system_service import recent_log

logs_bp = Blueprint("logs", __name__)
ACTION_LOG = Path("/var/log/epg_dashboard_actions.log")

@logs_bp.route("/")
def logs():
    action_logs = "No dashboard action log yet."
    if ACTION_LOG.exists():
        action_logs = ACTION_LOG.read_text(encoding="utf-8")[-12000:]

    return render_template(
        "logs.html",
        logs=recent_log(200),
        action_logs=action_logs
    )
