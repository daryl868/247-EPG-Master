from pathlib import Path
import subprocess
import json

ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = Path("/var/log/epg_auto_update.log")

def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    return result.stdout.strip() + ("\n" + result.stderr.strip() if result.stderr.strip() else "")

def git_status():
    return run_cmd(["git", "status", "--short"]) or "Clean"

def git_branch():
    return run_cmd(["git", "branch", "--show-current"]) or "unknown"

def git_last_commit():
    return run_cmd(["git", "log", "--oneline", "-1"]) or "unknown"

def recent_log(lines=80):
    if not LOG_FILE.exists():
        return "No automation log found yet."
    return run_cmd(["tail", f"-{lines}", str(LOG_FILE)])

def xml_files():
    return sorted([p.name for p in (ROOT / "generated").glob("*.xml")])

def provider_files():
    return sorted([p.name for p in (ROOT / "providers").glob("*.json")])

def provider_summary():
    providers = []
    total_channels = 0
    total_ocr = 0

    for path in sorted((ROOT / "providers").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            channels = data.get("channels", [])
            ocr_enabled = len([c for c in channels if c.get("ocr_enabled")])

            total_channels += len(channels)
            total_ocr += ocr_enabled

            providers.append({
                "file": path.name,
                "label": data.get("label", path.stem),
                "channels": len(channels),
                "ocr_enabled": ocr_enabled,
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

    return providers, total_channels, total_ocr

def metadata_cache_count():
    cache_dir = ROOT / "data" / "metadata"
    if not cache_dir.exists():
        return 0
    return len(list(cache_dir.glob("*.json")))

def correction_count():
    corrections_file = ROOT / "config" / "title_corrections.json"
    if not corrections_file.exists():
        return 0

    try:
        data = json.loads(corrections_file.read_text(encoding="utf-8"))
        return len(data.get("corrections", {}))
    except Exception:
        return 0

def cron_status():
    output = run_cmd(["systemctl", "is-active", "cron"])
    return "Running" if output.strip() == "active" else output or "Unknown"
