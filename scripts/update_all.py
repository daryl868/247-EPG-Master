#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PROVIDERS = [
    "providers/peacock.json",
    # "providers/netflix.json",
    # "providers/apple.json",
    # "providers/hulu.json",
    # "providers/oneplay.json",
]

def run(cmd):
    print("\n" + "=" * 70)
    print("Running:", " ".join(cmd))
    print("=" * 70)
    subprocess.run(cmd, cwd=ROOT, check=True)

def main():
    run([sys.executable, "scripts/build_global_titles.py"])
    for provider in PROVIDERS:
        path = ROOT / provider
        if not path.exists():
            print(f"Skipping missing provider: {provider}")
            continue

        run([sys.executable, "scripts/update_provider_ocr.py", provider])

    print("\nValidating XML...")
    validate_script = ROOT / "scripts/validate_xml.py"

    if validate_script.exists():
        run([sys.executable, "scripts/validate_xml.py"])
    else:
        print("No validate script found. Skipping validation.")

    print("\nAll provider OCR updates completed.")

if __name__ == "__main__":
    main()
