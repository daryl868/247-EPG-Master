#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(cmd, check=True):
    print("\n" + "=" * 70)
    print("Running:", " ".join(cmd))
    print("=" * 70)
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True, capture_output=False)

def has_changes():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True
    )
    return bool(result.stdout.strip())

def main():
    run([sys.executable, "scripts/update_all.py"])

    if not has_changes():
        print("\nNo changes detected. Nothing to publish.")
        return

    run(["git", "add", "config/global_titles.json"])
    run(["git", "add", "providers"])
    run(["git", "add", "generated"])
    run(["git", "add", "scripts"])
    run(["git", "add", "ocr"])
    run(["git", "add", "processing"])
    run(["git", "add", "xmltv"])

    commit_msg = "Auto update OCR EPG data"

    commit = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=ROOT,
        text=True
    )

    if commit.returncode != 0:
        print("No commit created.")
        return

    run(["git", "pull", "--rebase", "origin", "main"])
    run(["git", "push"])

    print("\nEPG update published successfully.")

if __name__ == "__main__":
    main()
