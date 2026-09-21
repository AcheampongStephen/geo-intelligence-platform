from pathlib import Path

import geopandas as gpd

HOSPITALS_PATH = Path("data/curated/hospitals_clean.parquet")

PHARMACIES_PATH = Path("data/processed/pharmacies.parquet")

OUTPUT_PATH = Path("data/curated/pharmacy_coverage.parquet")


PROJECTED_CRS = "EPSG:32617"


def classify_coverage(
    pharmacies_1km,
    pharmacies_2km,
    pharmacies_5km,
):
    """
    Classify pharmacy coverage around a hospital.

    These categories are project-defined analytical
    classifications, not medical or healthcare ratings.
    """

    if pharmacies_1km == 0 and pharmacies_2km == 0:
        return "LOW"

    if pharmacies_1km == 0:
        return "MODERATE"

    if pharmacies_1km >= 2:
        return "HIGH"

    return "GOOD"


def calculate_coverage(
    hospitals,
    pharmacies,
    radius_meters,
):
    """
    Calculate the number of pharmacies within
    the specified radius of each hospital.

    Distances are calculated directly between
    projected geometries in meters.
    """

    counts = {}

    for _, hospital in hospitals.iterrows():
        distances = pharmacies.geometry.distance(hospital.geometry)

        pharmacy_count = (distances <= radius_meters).sum()

        counts[hospital["osm_id"]] = int(pharmacy_count)

    return counts


def main():

    print("Loading datasets...")

    hospitals = gpd.read_parquet(HOSPITALS_PATH)

    pharmacies = gpd.read_parquet(PHARMACIES_PATH)

    print(f"Hospitals loaded: {len(hospitals)}")

    print(f"Pharmacies loaded: {len(pharmacies)}")

    # --------------------------------
    # Project both datasets into a
    # meter-based CRS.
    #
    # EPSG:32617 = WGS84 / UTM Zone 17N
    # --------------------------------

    hospitals = hospitals.to_crs(PROJECTED_CRS)

    pharmacies = pharmacies.to_crs(PROJECTED_CRS)

    print(f"\nDistance CRS: {PROJECTED_CRS}")

    # --------------------------------
    # Calculate 1 km coverage.
    # --------------------------------

    print("\nCalculating 1 km coverage...")

    coverage_1km = calculate_coverage(
        hospitals,
        pharmacies,
        1000,
    )

    # --------------------------------
    # Calculate 2 km coverage.
    # --------------------------------

    print("Calculating 2 km coverage...")

    coverage_2km = calculate_coverage(
        hospitals,
        pharmacies,
        2000,
    )

    # --------------------------------
    # Calculate 5 km coverage.
    # --------------------------------

    print("Calculating 5 km coverage...")

    coverage_5km = calculate_coverage(
        hospitals,
        pharmacies,
        5000,
    )

    # --------------------------------
    # Build result dataset.
    # --------------------------------

    result = hospitals[
        [
            "osm_id",
            "name",
            "city",
            "state",
            "latitude",
            "longitude",
            "geometry",
        ]
    ].copy()

    result = result.rename(
        columns={
            "osm_id": "hospital_osm_id",
            "name": "hospital_name",
        }
    )

    # --------------------------------
    # Add coverage counts.
    # --------------------------------

    result["pharmacies_within_1km"] = (
        result["hospital_osm_id"].map(coverage_1km).fillna(0).astype(int)
    )

    result["pharmacies_within_2km"] = (
        result["hospital_osm_id"].map(coverage_2km).fillna(0).astype(int)
    )

    result["pharmacies_within_5km"] = (
        result["hospital_osm_id"].map(coverage_5km).fillna(0).astype(int)
    )

    # --------------------------------
    # Classify coverage.
    # --------------------------------

    result["coverage_category"] = result.apply(
        lambda row: classify_coverage(
            row["pharmacies_within_1km"],
            row["pharmacies_within_2km"],
            row["pharmacies_within_5km"],
        ),
        axis=1,
    )

    # --------------------------------
    # Convert geometry back to WGS84.
    # --------------------------------

    result = result.to_crs("EPSG:4326")

    # --------------------------------
    # Save output.
    # --------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    # --------------------------------
    # Display results.
    # --------------------------------

    print("\nHospital Pharmacy Coverage")

    print("=" * 100)

    display_columns = [
        "hospital_name",
        "pharmacies_within_1km",
        "pharmacies_within_2km",
        "pharmacies_within_5km",
        "coverage_category",
    ]

    print(result[display_columns].to_string(index=False))

    print("=" * 100)

    # --------------------------------
    # Validation check.
    #
    # A hospital with no pharmacy within
    # 5 km must show zero.
    # --------------------------------

    zero_5km = result[result["pharmacies_within_5km"] == 0]

    print("\nHospitals with zero pharmacies within 5 km:")

    if zero_5km.empty:
        print("None")

    else:
        for _, row in zero_5km.iterrows():
            print(f"  - {row['hospital_name']}")

    print(f"\nCoverage analysis saved to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
