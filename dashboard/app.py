from pathlib import Path
import json
from flask import Flask, render_template

ROOT = Path(__file__).resolve().parents[1]
app = Flask(__name__)

@app.route("/")
def index():
    idx = json.loads((ROOT / "config/providers.json").read_text())
    providers = []
    for p in idx["providers"]:
        data = json.loads((ROOT / p["path"]).read_text())
        providers.append({"label": data["label"], "channels": len(data["channels"]), "xml": data["output_xml"], "m3u": data["output_m3u"]})
    return render_template("index.html", providers=providers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
