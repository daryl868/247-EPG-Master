#!/usr/bin/env python3
from flask import Flask
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
