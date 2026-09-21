import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

RAW_DATA_PATH = Path("data/raw/pharmacies.json")
PROCESSED_DATA_PATH = Path("data/processed/pharmacies.parquet")


def load_raw_data():
    with RAW_DATA_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def extract_pharmacies(data):
    pharmacies = []

    for element in data["elements"]:
        tags = element.get("tags", {})

        if element["type"] == "node":
            latitude = element.get("lat")
            longitude = element.get("lon")
        else:
            center = element.get("center", {})
            latitude = center.get("lat")
            longitude = center.get("lon")

        if latitude is None or longitude is None:
            continue

        pharmacy = {
            "osm_type": element["type"],
            "osm_id": element["id"],
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "operator": tags.get("operator"),
            "website": tags.get("website"),
            "phone": tags.get("phone"),
            "address": tags.get("addr:street"),
            "city": tags.get("addr:city"),
            "state": tags.get("addr:state"),
            "postcode": tags.get("addr:postcode"),
            "latitude": latitude,
            "longitude": longitude,
        }

        pharmacies.append(pharmacy)

    return pharmacies


def create_geodataframe(pharmacies):
    df = pd.DataFrame(pharmacies)

    geometry = [
        Point(longitude, latitude)
        for longitude, latitude in zip(
            df["longitude"],
            df["latitude"],
        )
    ]

    return gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs="EPSG:4326",
    )


def main():
    print("Loading raw pharmacy data...")

    data = load_raw_data()

    print(f"Raw OSM objects: {len(data['elements'])}")

    pharmacies = extract_pharmacies(data)

    print(f"Objects with coordinates: {len(pharmacies)}")

    gdf = create_geodataframe(pharmacies)

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    gdf.to_parquet(
        PROCESSED_DATA_PATH,
        index=False,
    )

    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")

    print("\nDataset preview:")

    print(
        gdf[
            [
                "osm_type",
                "osm_id",
                "name",
                "city",
                "state",
                "latitude",
                "longitude",
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()
