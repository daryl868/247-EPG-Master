#!/usr/bin/env python3
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def xmltv_time(dt, tz_offset):
    return dt.strftime("%Y%m%d%H%M%S") + " " + tz_offset

def channel_xml(ch, logo):
    lines = [
        f'  <channel id="{escape(ch["id"])}">',
        f'    <display-name>{escape(ch["name"])}</display-name>',
    ]
    if logo:
        lines.append(f'    <icon src="{escape(logo)}" />')
    lines.append("  </channel>")
    return lines

def programme_xml(ch, start, stop, tz_offset):
    title = ch.get("show") or ch["name"]
    lines = [
        f'  <programme start="{xmltv_time(start, tz_offset)}" stop="{xmltv_time(stop, tz_offset)}" channel="{escape(ch["id"])}">',
        f'    <title>{escape(title)}</title>',
    ]
    if ch.get("subtitle"):
        lines.append(f'    <sub-title>{escape(ch["subtitle"])}</sub-title>')
    lines.append("    <desc>24/7 channel</desc>")
    lines.append("  </programme>")
    return lines

def build_provider(provider, settings):
    out_dir = ROOT / settings["generated_dir"]
    logo = provider.get("logo", settings.get("default_logo", ""))
    tz_offset = settings["timezone_offset"]
    days = int(settings["days"])
    block_hours = int(settings.get("programme_block_hours", 1))
    start_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', f'<tv generator-info-name="{escape(provider["label"])}">']
    for ch in provider["channels"]:
        xml.extend(channel_xml(ch, logo))

    for hour in range(0, days * 24, block_hours):
        start = start_day + timedelta(hours=hour)
        stop = start + timedelta(hours=block_hours)
        for ch in provider["channels"]:
            xml.extend(programme_xml(ch, start, stop, tz_offset))
    xml.append("</tv>")

    xml_path = out_dir / provider["output_xml"]
    write_text(xml_path, "\n".join(xml))
    ET.parse(xml_path)

    m3u = ["#EXTM3U"]
    group = provider.get("group_title", provider["label"])
    for ch in provider["channels"]:
        if not ch.get("stream_url"):
            continue
        m3u.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{logo}" group-title="{group}",{ch["name"]}')
        m3u.append(ch["stream_url"])
    write_text(out_dir / provider["output_m3u"], "\n".join(m3u) + "\n")

    return xml_path

def main():
    settings = load_json(ROOT / "config/settings.json")
    index = load_json(ROOT / "config/providers.json")
    out_dir = ROOT / settings["generated_dir"]

    combined_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="EPG Vision Combined">']
    combined_m3u = ["#EXTM3U"]

    for item in index["providers"]:
        provider = load_json(ROOT / item["path"])
        xml_path = build_provider(provider, settings)

        lines = xml_path.read_text(encoding="utf-8").splitlines()
        body = [line for line in lines if not line.startswith("<?xml") and not line.startswith("<tv") and line.strip() != "</tv>"]
        combined_xml.extend(body)

        m3u_path = out_dir / provider["output_m3u"]
        if m3u_path.exists():
            m3u_lines = m3u_path.read_text(encoding="utf-8").splitlines()
            combined_m3u.extend([line for line in m3u_lines if line != "#EXTM3U"])

    combined_xml.append("</tv>")
    combined_xml_path = out_dir / settings["combined_xml"]
    write_text(combined_xml_path, "\n".join(combined_xml))
    ET.parse(combined_xml_path)

    write_text(out_dir / settings["combined_m3u"], "\n".join(combined_m3u) + "\n")

    print(f"Generated XMLTV/M3U in {out_dir}")

if __name__ == "__main__":
    main()
