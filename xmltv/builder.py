from datetime import datetime, timedelta
from html import escape
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from metadata.service import MetadataService

metadata = MetadataService()
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def xmltv_time(dt, tz):
    return dt.strftime("%Y%m%d%H%M%S") + " " + tz


def enrich_title(title):
    try:
        return metadata.lookup(title)
    except Exception:
        return None


def build_provider(provider, settings):
    out = ROOT / settings["generated_dir"]
    out.mkdir(parents=True, exist_ok=True)

    tz = settings["timezone_offset"]
    days = int(settings["days"])
    block = int(settings.get("programme_block_hours", 24))
    start_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logo = provider.get("logo", "")

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<tv generator-info-name="{escape(provider["label"])}">'
    ]

    info = provider.get("info_channel")
    all_channels = ([info] if info else []) + provider["channels"]

    for item in all_channels:
        xml.append(f'  <channel id="{escape(item["id"])}">')
        xml.append(f'    <display-name>{escape(item["name"])}</display-name>')
        if logo:
            xml.append(f'    <icon src="{escape(logo)}" />')
        xml.append("  </channel>")

    for hour in range(0, days * 24, block):
        start = start_day + timedelta(hours=hour)
        stop = start + timedelta(hours=block)

        if info:
            desc = "\n".join([
                f"{i}. {ch.get('show','')} - {ch.get('subtitle','')}".strip()
                for i, ch in enumerate(provider["channels"], 1)
            ])

            xml.extend([
                f'  <programme start="{xmltv_time(start, tz)}" stop="{xmltv_time(stop, tz)}" channel="{escape(info["id"])}">',
                "    <title>Current Lineup</title>",
                f"    <desc>{escape(desc)}</desc>",
                "  </programme>"
            ])

        for ch in provider["channels"]:
            show = ch.get("show") or ch["name"]
            meta = enrich_title(show)

            final_title = show
            desc = "24/7 channel"
            date = ""
            icon = ""

            if meta:
                final_title = meta.get("title") or show
                desc = meta.get("overview") or desc
                release_date = meta.get("release_date", "")
                if release_date:
                    date = release_date[:4]
                if meta.get("poster"):
                    icon = IMAGE_BASE + meta["poster"]

            xml.append(
                f'  <programme start="{xmltv_time(start, tz)}" stop="{xmltv_time(stop, tz)}" channel="{escape(ch["id"])}">'
            )
            xml.append(f"    <title>{escape(final_title)}</title>")

            if ch.get("subtitle"):
                xml.append(f'    <sub-title>{escape(ch["subtitle"])}</sub-title>')

            if date:
                xml.append(f"    <date>{escape(date)}</date>")

            xml.append(f"    <desc>{escape(desc)}</desc>")

            if icon:
                xml.append(f'    <icon src="{escape(icon)}" />')

            xml.append("  </programme>")

    xml.append("</tv>")

    path = out / provider["output_xml"]
    path.write_text("\n".join(xml), encoding="utf-8")
    ET.parse(path)

    m3u = ["#EXTM3U"]
    group = provider.get("group_title", provider["label"])

    for item in all_channels:
        if item.get("stream_url"):
            m3u.append(
                f'#EXTINF:-1 tvg-id="{item["id"]}" tvg-name="{item["name"]}" tvg-logo="{logo}" group-title="{group}",{item["name"]}'
            )
            m3u.append(item["stream_url"])

    (out / provider["output_m3u"]).write_text("\n".join(m3u) + "\n", encoding="utf-8")

    return path


def build_all():
    settings = load_json(ROOT / "config/settings.json")
    index = load_json(ROOT / "config/providers.json")
    out = ROOT / settings["generated_dir"]

    combined_xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<tv generator-info-name="EPG Vision Studio">'
    ]
    combined_m3u = ["#EXTM3U"]

    for p in index["providers"]:
        provider = load_json(ROOT / p["path"])
        xml_path = build_provider(provider, settings)

        lines = xml_path.read_text(encoding="utf-8").splitlines()
        combined_xml.extend([
            line for line in lines
            if not line.startswith("<?xml")
            and not line.startswith("<tv")
            and line.strip() != "</tv>"
        ])

        m3u_path = out / provider["output_m3u"]
        combined_m3u.extend([
            line for line in m3u_path.read_text(encoding="utf-8").splitlines()
            if line != "#EXTM3U"
        ])

    combined_xml.append("</tv>")

    combined_xml_path = out / settings["combined_xml"]
    combined_xml_path.write_text("\n".join(combined_xml), encoding="utf-8")
    ET.parse(combined_xml_path)

    (out / settings["combined_m3u"]).write_text("\n".join(combined_m3u) + "\n", encoding="utf-8")

    print("EPG build complete.")


if __name__ == "__main__":
    build_all()
