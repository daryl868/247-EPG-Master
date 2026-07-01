#!/usr/bin/env python3

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

providers = ROOT / "providers"
output = ROOT / "config" / "global_titles.json"

titles = set()

for provider in providers.glob("*.json"):

    data = json.loads(
        provider.read_text(encoding="utf-8")
    )

    print(f"Scanning {provider.name}")

    for channel in data.get("channels", []):

        show = channel.get("show", "").strip()

        if show:
            titles.add(show)

        for history in channel.get("history", []):

            if history.get("old"):
                titles.add(history["old"])

            if history.get("new"):
                titles.add(history["new"])

titles = sorted(titles)

output.write_text(
    json.dumps(
        {
            "generated": len(titles),
            "titles": titles
        },
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print()
print(f"Generated {len(titles)} titles")
print(output)
