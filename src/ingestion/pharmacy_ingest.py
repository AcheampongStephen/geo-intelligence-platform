import json
from pathlib import Path

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

QUERY = """
[out:json][timeout:60];

(
  node["amenity"="pharmacy"](33.8,-81.2,34.2,-80.7);
  way["amenity"="pharmacy"](33.8,-81.2,34.2,-80.7);
  relation["amenity"="pharmacy"](33.8,-81.2,34.2,-80.7);
);

out center;
"""

RAW_DATA_PATH = Path("data/raw/pharmacies.json")


def fetch_osm_data():
    headers = {
        "User-Agent": ("GeoIntelligencePlatform/1.0 (Python; educational project)")
    }

    response = requests.post(
        OVERPASS_URL,
        data=QUERY,
        headers=headers,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def save_raw_data(data):
    RAW_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with RAW_DATA_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
        )


def main():
    data = fetch_osm_data()

    save_raw_data(data)

    print(f"Saved {len(data['elements'])} OSM pharmacy objects to {RAW_DATA_PATH}")


if __name__ == "__main__":
    main()
