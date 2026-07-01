from flask import Blueprint, render_template
from services.system_service import recent_log

logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/")
def logs():
    return render_template("logs.html", logs=recent_log(200))
