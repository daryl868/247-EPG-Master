#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from metadata.service import MetadataService

m = MetadataService()

info = m.lookup("The Burbs")

print(info)
