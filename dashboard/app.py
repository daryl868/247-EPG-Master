from pathlib import Path
import json
from flask import Flask, render_template

ROOT = Path(__file__).resolve().parents[1]
app = Flask(__name__)

@app.route("/")
def index():
    index = json.loads((ROOT / "config/providers.json").read_text())
    providers = []
    for item in index["providers"]:
        p = json.loads((ROOT / item["path"]).read_text())
        providers.append({
            "label": p["label"],
            "channels": len(p["channels"]),
            "output_xml": p["output_xml"],
            "output_m3u": p["output_m3u"]
        })
    return render_template("index.html", providers=providers)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
