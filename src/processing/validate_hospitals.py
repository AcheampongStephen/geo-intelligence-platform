import json
import sys
from pathlib import Path

import geopandas as gpd

DATA_PATH = Path("data/processed/hospitals.parquet")
CURATED_PATH = Path("data/curated/hospitals_clean.parquet")
REPORT_PATH = Path("data/curated/quality_report.json")


def add_check(checks, name, severity, count, details):
    checks.append(
        {
            "check": name,
            "severity": severity,
            "count": int(count),
            "details": details,
        }
    )


def main():
    print("Loading processed hospital dataset...")

    gdf = gpd.read_parquet(DATA_PATH)

    print(f"Total records: {len(gdf)}")

    checks = []

    # -----------------------------
    # ERROR CHECKS
    # -----------------------------

    missing_names = gdf["name"].isna().sum()

    add_check(
        checks,
        "missing_names",
        "ERROR",
        missing_names,
        "Hospital records without a name",
    )

    missing_latitude = gdf["latitude"].isna().sum()

    add_check(
        checks,
        "missing_latitude",
        "ERROR",
        missing_latitude,
        "Records without latitude",
    )

    missing_longitude = gdf["longitude"].isna().sum()

    add_check(
        checks,
        "missing_longitude",
        "ERROR",
        missing_longitude,
        "Records without longitude",
    )

    invalid_latitude = ((gdf["latitude"] < -90) | (gdf["latitude"] > 90)).sum()

    add_check(
        checks,
        "invalid_latitude",
        "ERROR",
        invalid_latitude,
        "Latitude outside valid range",
    )

    invalid_longitude = ((gdf["longitude"] < -180) | (gdf["longitude"] > 180)).sum()

    add_check(
        checks,
        "invalid_longitude",
        "ERROR",
        invalid_longitude,
        "Longitude outside valid range",
    )

    duplicate_ids = gdf["osm_id"].duplicated().sum()

    add_check(
        checks,
        "duplicate_osm_ids",
        "ERROR",
        duplicate_ids,
        "Duplicate OpenStreetMap IDs",
    )

    invalid_geometry = (~gdf.geometry.is_valid).sum()

    add_check(
        checks,
        "invalid_geometry",
        "ERROR",
        invalid_geometry,
        "Invalid geographic geometry",
    )

    # -----------------------------
    # WARNING CHECKS
    # -----------------------------

    missing_city = gdf["city"].isna().sum()

    add_check(
        checks,
        "missing_city",
        "WARNING",
        missing_city,
        "Records without city information",
    )

    missing_state = gdf["state"].isna().sum()

    add_check(
        checks,
        "missing_state",
        "WARNING",
        missing_state,
        "Records without state information",
    )

    duplicate_coordinates = gdf.duplicated(subset=["latitude", "longitude"]).sum()

    add_check(
        checks,
        "duplicate_coordinates",
        "WARNING",
        duplicate_coordinates,
        "Records sharing identical coordinates",
    )

    # -----------------------------
    # DETERMINE PIPELINE STATUS
    # -----------------------------

    errors = [
        check for check in checks if check["severity"] == "ERROR" and check["count"] > 0
    ]

    warnings = [
        check
        for check in checks
        if check["severity"] == "WARNING" and check["count"] > 0
    ]

    status = "PASS" if not errors else "FAIL"

    # -----------------------------
    # CREATE REPORT
    # -----------------------------

    report = {
        "dataset": "hospitals",
        "record_count": len(gdf),
        "status": status,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    # -----------------------------
    # CREATE CURATED DATASET
    # -----------------------------

    if status == "PASS":
        curated = gdf[
            gdf["name"].notna()
            & gdf["latitude"].notna()
            & gdf["longitude"].notna()
            & gdf.geometry.notna()
            & gdf.geometry.is_valid
        ].copy()

        curated.to_parquet(
            CURATED_PATH,
            index=False,
        )

        print(f"\nCurated dataset saved to:\n{CURATED_PATH}")

    # -----------------------------
    # DISPLAY RESULTS
    # -----------------------------

    print("\n==============================")
    print("DATA QUALITY REPORT")
    print("==============================")

    for check in checks:
        print(f"{check['severity']:7} {check['check']:25} {check['count']}")

    print("\n==============================")
    print(f"STATUS: {status}")
    print("==============================")

    print(f"\nQuality report saved to:\n{REPORT_PATH}")

    # -----------------------------
    # FAIL PIPELINE IF NECESSARY
    # -----------------------------

    if status == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
