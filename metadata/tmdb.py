import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]

config = json.loads(
    (ROOT / "config" / "tmdb.json").read_text()
)

API = config["api_key"]


def lookup(title):

    url = "https://api.themoviedb.org/3/search/tv"

    params = {
        "api_key": API,
        "query": title,
        "language": "en-US",
        "include_adult": False
    }

    r = requests.get(url, params=params, timeout=20)

    r.raise_for_status()

    results = r.json()["results"]

    if not results:
        return None

    best = results[0]

    return {
        "tmdb_id": best["id"],
        "media_type": "tv",
        "title": best.get("title") or best.get("name"),
        "overview": best.get("overview", ""),
        "poster": best.get("poster_path"),
        "backdrop": best.get("backdrop_path"),
        "release_date": best.get(
            "release_date",
            best.get("first_air_date", "")
        )
    }
