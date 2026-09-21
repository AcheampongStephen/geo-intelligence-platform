from pathlib import Path

import geopandas as gpd

HOSPITALS_PATH = Path("data/curated/hospitals_clean.parquet")

PHARMACIES_PATH = Path("data/processed/pharmacies.parquet")

PROJECTED_CRS = "EPSG:32617"


def main():

    print("Loading datasets...")

    hospitals = gpd.read_parquet(HOSPITALS_PATH)

    pharmacies = gpd.read_parquet(PHARMACIES_PATH)

    print(f"Hospitals: {len(hospitals)}")

    print(f"Pharmacies: {len(pharmacies)}")

    print("\nOriginal CRS:")
    print(f"Hospitals: {hospitals.crs}")
    print(f"Pharmacies: {pharmacies.crs}")

    # --------------------------------
    # Project both datasets into meters.
    # --------------------------------

    hospitals = hospitals.to_crs(PROJECTED_CRS)

    pharmacies = pharmacies.to_crs(PROJECTED_CRS)

    print("\nProjected CRS:")
    print(f"Hospitals: {hospitals.crs}")
    print(f"Pharmacies: {pharmacies.crs}")

    # --------------------------------
    # Find the specific hospital.
    # --------------------------------

    hospital = hospitals[
        hospitals["name"] == "Midlands Regional Rehabilitation Hospital"
    ]

    if hospital.empty:
        print("\nHospital not found.")
        return

    hospital_row = hospital.iloc[0]

    print("\nHospital:")
    print(hospital_row["name"])

    print(f"Hospital OSM ID: {hospital_row['osm_id']}")

    print(f"Geometry: {hospital_row.geometry}")

    # --------------------------------
    # Calculate distance from this
    # hospital to EVERY pharmacy.
    # --------------------------------

    pharmacies = pharmacies.copy()

    pharmacies["distance_meters"] = pharmacies.geometry.distance(hospital_row.geometry)

    pharmacies["distance_km"] = pharmacies["distance_meters"] / 1000

    # --------------------------------
    # Sort nearest → farthest.
    # --------------------------------

    nearest = pharmacies.sort_values("distance_meters")

    print("\nNearest pharmacies:")

    print("=" * 80)

    columns = [
        "osm_id",
        "name",
        "distance_meters",
        "distance_km",
    ]

    print(nearest[columns].head(10).to_string(index=False))

    print("=" * 80)

    # --------------------------------
    # Count pharmacies within each
    # radius directly.
    # --------------------------------

    within_1km = (nearest["distance_meters"] <= 1000).sum()

    within_2km = (nearest["distance_meters"] <= 2000).sum()

    within_5km = (nearest["distance_meters"] <= 5000).sum()

    print("\nDirect distance calculation:")

    print(f"Within 1 km: {within_1km}")

    print(f"Within 2 km: {within_2km}")

    print(f"Within 5 km: {within_5km}")

    print(f"Nearest pharmacy: {nearest.iloc[0]['distance_km']:.2f} km")


if __name__ == "__main__":
    main()
