import geopandas as gpd
from shapely.geometry import Point

from src.analytics.pharmacy_coverage import (
    calculate_coverage,
    classify_coverage,
)


def test_classify_coverage_low():
    assert classify_coverage(0, 0, 0) == "LOW"
    assert classify_coverage(0, 0, 4) == "LOW"


def test_classify_coverage_moderate():
    assert classify_coverage(0, 1, 1) == "MODERATE"
    assert classify_coverage(0, 2, 7) == "MODERATE"


def test_classify_coverage_good():
    assert classify_coverage(1, 1, 3) == "GOOD"


def test_classify_coverage_high():
    assert classify_coverage(2, 2, 7) == "HIGH"
    assert classify_coverage(3, 3, 10) == "HIGH"


def test_calculate_coverage_counts_pharmacies_inside_radius():
    hospitals = gpd.GeoDataFrame(
        {
            "osm_id": [1],
            "geometry": [Point(0, 0)],
        },
        crs="EPSG:32617",
    )

    pharmacies = gpd.GeoDataFrame(
        {
            "osm_id": [101, 102, 103],
            "geometry": [
                Point(500, 0),
                Point(1000, 0),
                Point(1500, 0),
            ],
        },
        crs="EPSG:32617",
    )

    result = calculate_coverage(
        hospitals,
        pharmacies,
        radius_meters=1000,
    )

    assert result == {1: 2}


def test_calculate_coverage_returns_zero_when_none_inside_radius():
    hospitals = gpd.GeoDataFrame(
        {
            "osm_id": [1],
            "geometry": [Point(0, 0)],
        },
        crs="EPSG:32617",
    )

    pharmacies = gpd.GeoDataFrame(
        {
            "osm_id": [101, 102],
            "geometry": [
                Point(1500, 0),
                Point(2000, 0),
            ],
        },
        crs="EPSG:32617",
    )

    result = calculate_coverage(
        hospitals,
        pharmacies,
        radius_meters=1000,
    )

    assert result == {1: 0}
