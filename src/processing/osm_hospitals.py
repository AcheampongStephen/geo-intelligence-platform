import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

RAW_DATA_PATH = Path("data/raw/hospitals.json")
PROCESSED_DATA_PATH = Path("data/processed/hospitals.parquet")


def load_raw_data():
    with RAW_DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_hospitals(data):
    hospitals = []

    for element in data["elements"]:
        tags = element.get("tags", {})

        # Nodes have their coordinates directly.
        if element["type"] == "node":
            latitude = element.get("lat")
            longitude = element.get("lon")

        # Ways and relations returned with "out center"
        # contain representative coordinates under "center".
        else:
            center = element.get("center", {})
            latitude = center.get("lat")
            longitude = center.get("lon")

        # Skip anything without coordinates.
        if latitude is None or longitude is None:
            continue

        hospital = {
            "osm_type": element["type"],
            "osm_id": element["id"],
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "emergency": tags.get("emergency"),
            "healthcare": tags.get("healthcare"),
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

        hospitals.append(hospital)

    return hospitals


def create_geodataframe(hospitals):
    df = pd.DataFrame(hospitals)

    geometry = [
        Point(longitude, latitude)
        for longitude, latitude in zip(df["longitude"], df["latitude"])
    ]

    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs="EPSG:4326",
    )

    return gdf


def save_processed_data(gdf):
    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    gdf.to_parquet(
        PROCESSED_DATA_PATH,
        index=False,
    )


def main():
    print("Loading raw OSM data...")

    data = load_raw_data()

    print(f"Raw OSM objects: {len(data['elements'])}")

    hospitals = extract_hospitals(data)

    print(f"Objects with coordinates: {len(hospitals)}")

    gdf = create_geodataframe(hospitals)

    save_processed_data(gdf)

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
