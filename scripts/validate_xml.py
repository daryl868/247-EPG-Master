#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []
for path in (ROOT / "generated").glob("*.xml"):
    try:
        ET.parse(path)
        print(f"OK {path.name}")
    except Exception as e:
        errors.append((path.name, str(e)))
        print(f"ERROR {path.name}: {e}")

if errors:
    raise SystemExit(1)
