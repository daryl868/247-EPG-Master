#!/usr/bin/env python3
from flask import Flask

from routes.dashboard import dashboard_bp
from routes.providers import providers_bp
from routes.logs import logs_bp
from routes.actions import actions_bp
from routes.ocr import ocr_bp

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
