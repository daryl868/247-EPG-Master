#!/usr/bin/env python3
from flask import Flask, send_from_directory
from pathlib import Path

from routes.dashboard import dashboard_bp
from routes.providers import providers_bp
from routes.logs import logs_bp
from routes.actions import actions_bp
from routes.ocr import ocr_bp
from routes.operations import operations_bp

ROOT = Path(__file__).resolve().parents[1]

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.register_blueprint(dashboard_bp)
app.register_blueprint(providers_bp, url_prefix="/providers")
app.register_blueprint(logs_bp, url_prefix="/logs")
app.register_blueprint(actions_bp, url_prefix="/actions")
app.register_blueprint(ocr_bp, url_prefix="/ocr")
app.register_blueprint(operations_bp, url_prefix="/operations")

@app.route("/debug/<path:filename>")
def debug_files(filename):
    return send_from_directory(ROOT / "debug", filename)

@app.route("/data/screenshots/<path:filename>")
def screenshot_files(filename):
    return send_from_directory(ROOT / "data" / "screenshots", filename)

@app.route("/data/crops/<path:filename>")
def crop_files(filename):
    return send_from_directory(ROOT / "data" / "crops", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
