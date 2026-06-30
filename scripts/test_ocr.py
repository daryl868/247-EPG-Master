#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ocr.engine import test_channel

def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "providers/peacock.json"
    channel_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    result = test_channel(provider, channel_index)
    print(f"Channel:  {result['channel']}")
    print(f"Expected: {result['expected']}\n")
    for r in result["results"]:
        print(f"Frame {r['frame']} @ {r['second']}s")
        print(f"Raw:        {r['raw']}")
        print(f"Clean:      {r['clean']}")
        print(f"Confidence: {r['confidence']}")
        print(f"Crop:       {r['crop']}\n")
    print("Best Result")
    print("-----------")
    print(result["best"].get("clean", ""))
    print(result["best"].get("confidence", ""))

if __name__ == "__main__":
    main()
