#!/usr/bin/env python3
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocr.engine import test_channel

provider_arg = sys.argv[1] if len(sys.argv) > 1 else "providers/peacock.json"
channel_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0

result = test_channel(provider_arg, channel_index)

print(json.dumps(result, indent=2, ensure_ascii=False))
