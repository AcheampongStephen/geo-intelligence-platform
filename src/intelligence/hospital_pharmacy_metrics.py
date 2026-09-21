from pathlib import Path

import geopandas as gpd
import pandas as pd

HOSPITAL_PHARMACY_PATH = Path("data/curated/hospital_pharmacy_analysis.parquet")

COVERAGE_PATH = Path("data/curated/pharmacy_coverage.parquet")

OUTPUT_PATH = Path("data/curated/hospital_pharmacy_metrics.parquet")


def calculate_accessibility_score(row):
    """
    Transparent 0-100 accessibility score.

    Components:
    - Nearest pharmacy distance: 40 points
    - Pharmacies within 1 km: 30 points
    - Pharmacies within 5 km: 30 points
    """

    # --------------------------------------------------------------
    # Distance component: 40 points
    # --------------------------------------------------------------

    distance_km = row["nearest_pharmacy_km"]

    if pd.isna(distance_km):
        distance_score = 0
    elif distance_km <= 1:
        distance_score = 40
    elif distance_km <= 2:
        distance_score = 30
    elif distance_km <= 5:
        distance_score = 20
    elif distance_km <= 10:
        distance_score = 10
    else:
        distance_score = 0

    # --------------------------------------------------------------
    # 1 km pharmacy component: 30 points
    # --------------------------------------------------------------

    pharmacies_1km = row["pharmacies_within_1km"]

    if pharmacies_1km >= 3:
        pharmacy_1km_score = 30
    elif pharmacies_1km == 2:
        pharmacy_1km_score = 25
    elif pharmacies_1km == 1:
        pharmacy_1km_score = 15
    else:
        pharmacy_1km_score = 0

    # --------------------------------------------------------------
    # 5 km pharmacy component: 30 points
    # --------------------------------------------------------------

    pharmacies_5km = row["pharmacies_within_5km"]

    if pharmacies_5km >= 10:
        pharmacy_5km_score = 30
    elif pharmacies_5km >= 5:
        pharmacy_5km_score = 25
    elif pharmacies_5km >= 2:
        pharmacy_5km_score = 15
    elif pharmacies_5km == 1:
        pharmacy_5km_score = 5
    else:
        pharmacy_5km_score = 0

    return distance_score + pharmacy_1km_score + pharmacy_5km_score


def classify_accessibility(score):
    if score >= 80:
        return "HIGH_ACCESS"

    if score >= 60:
        return "MODERATE_ACCESS"

    if score >= 40:
        return "LIMITED_ACCESS"

    return "LOW_ACCESS"


def main():
    print("Loading curated datasets...")

    nearest = gpd.read_parquet(HOSPITAL_PHARMACY_PATH)

    coverage = gpd.read_parquet(COVERAGE_PATH)

    print(f"Nearest pharmacy records: {len(nearest)}")

    print(f"Coverage records: {len(coverage)}")

    # ==============================================================
    # NORMALIZE NEAREST-PHARMACY SCHEMA
    # ==============================================================

    nearest = nearest[
        [
            "osm_id_hospital",
            "name_hospital",
            "nearest_pharmacy",
            "nearest_pharmacy_osm_id",
            "pharmacy_name_available",
            "distance_meters",
            "distance_km",
            "distance_category",
        ]
    ].copy()

    nearest = nearest.rename(
        columns={
            "osm_id_hospital": "hospital_osm_id",
            "name_hospital": "hospital_name",
            "distance_km": "nearest_pharmacy_km",
            "distance_category": "nearest_pharmacy_category",
        }
    )

    # ==============================================================
    # PREPARE COVERAGE DATASET
    # ==============================================================

    coverage = coverage[
        [
            "hospital_osm_id",
            "pharmacies_within_1km",
            "pharmacies_within_2km",
            "pharmacies_within_5km",
        ]
    ].copy()

    # ==============================================================
    # VALIDATE JOIN KEYS
    # ==============================================================

    if nearest["hospital_osm_id"].duplicated().any():
        raise ValueError(
            "Duplicate hospital_osm_id values found in nearest pharmacy dataset."
        )

    if coverage["hospital_osm_id"].duplicated().any():
        raise ValueError("Duplicate hospital_osm_id values found in coverage dataset.")

    # ==============================================================
    # MERGE
    # ==============================================================

    metrics = nearest.merge(
        coverage,
        on="hospital_osm_id",
        how="left",
        validate="one_to_one",
    )

    # ==============================================================
    # COVERAGE INDICATORS
    # ==============================================================

    metrics["coverage_1km"] = metrics["pharmacies_within_1km"] > 0

    metrics["coverage_2km"] = metrics["pharmacies_within_2km"] > 0

    metrics["coverage_5km"] = metrics["pharmacies_within_5km"] > 0

    # ==============================================================
    # ACCESSIBILITY SCORE
    # ==============================================================

    metrics["accessibility_score"] = metrics.apply(
        calculate_accessibility_score,
        axis=1,
    )

    metrics["accessibility_category"] = metrics["accessibility_score"].apply(
        classify_accessibility
    )

    # ==============================================================
    # DATA QUALITY FLAGS
    # ==============================================================

    metrics["nearest_pharmacy_name_available"] = metrics["nearest_pharmacy"].notna()

    metrics["has_pharmacy_within_5km"] = metrics["pharmacies_within_5km"] > 0

    # ==============================================================
    # OUTPUT
    # ==============================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics.to_parquet(
        OUTPUT_PATH,
        index=False,
    )

    # ==============================================================
    # DISPLAY RESULTS
    # ==============================================================

    print("\nHospital Pharmacy Intelligence")
    print("=" * 110)

    display_columns = [
        "hospital_name",
        "nearest_pharmacy_km",
        "pharmacies_within_1km",
        "pharmacies_within_2km",
        "pharmacies_within_5km",
        "accessibility_score",
        "accessibility_category",
    ]

    print(
        metrics[display_columns]
        .sort_values("accessibility_score")
        .to_string(index=False)
    )

    print("=" * 110)

    # ==============================================================
    # DATASET SUMMARY
    # ==============================================================

    total_hospitals = len(metrics)

    print("\nDataset Metrics")
    print("-" * 60)

    print(f"Total hospitals: {total_hospitals}")

    print(f"Hospitals with pharmacy within 1 km: {metrics['coverage_1km'].sum()}")

    print(f"Hospitals with pharmacy within 2 km: {metrics['coverage_2km'].sum()}")

    print(f"Hospitals with pharmacy within 5 km: {metrics['coverage_5km'].sum()}")

    print(
        "Average nearest pharmacy distance: "
        f"{metrics['nearest_pharmacy_km'].mean():.2f} km"
    )

    print(
        "Maximum nearest pharmacy distance: "
        f"{metrics['nearest_pharmacy_km'].max():.2f} km"
    )

    print("\nAccessibility categories:")

    print(metrics["accessibility_category"].value_counts().to_string())

    print(f"\nMetrics saved to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
