import pandas as pd
import pytest

from src.intelligence.hospital_pharmacy_metrics import (
    calculate_accessibility_score,
    classify_accessibility,
)


@pytest.mark.parametrize(
    ("distance_km", "expected_score"),
    [
        (0.5, 40),
        (1.0, 40),
        (1.5, 30),
        (2.0, 30),
        (3.0, 20),
        (5.0, 20),
        (7.0, 10),
        (10.0, 10),
        (11.0, 0),
        (float("nan"), 0),
    ],
)
def test_accessibility_distance_component(
    distance_km,
    expected_score,
):
    row = pd.Series(
        {
            "nearest_pharmacy_km": distance_km,
            "pharmacies_within_1km": 0,
            "pharmacies_within_5km": 0,
        }
    )

    assert calculate_accessibility_score(row) == expected_score


@pytest.mark.parametrize(
    ("pharmacies_1km", "expected_score"),
    [
        (0, 0),
        (1, 15),
        (2, 25),
        (3, 30),
        (10, 30),
    ],
)
def test_accessibility_one_km_component(
    pharmacies_1km,
    expected_score,
):
    row = pd.Series(
        {
            "nearest_pharmacy_km": float("nan"),
            "pharmacies_within_1km": pharmacies_1km,
            "pharmacies_within_5km": 0,
        }
    )

    assert calculate_accessibility_score(row) == expected_score


@pytest.mark.parametrize(
    ("pharmacies_5km", "expected_score"),
    [
        (0, 0),
        (1, 5),
        (2, 15),
        (4, 15),
        (5, 25),
        (9, 25),
        (10, 30),
        (20, 30),
    ],
)
def test_accessibility_five_km_component(
    pharmacies_5km,
    expected_score,
):
    row = pd.Series(
        {
            "nearest_pharmacy_km": float("nan"),
            "pharmacies_within_1km": 0,
            "pharmacies_within_5km": pharmacies_5km,
        }
    )

    assert calculate_accessibility_score(row) == expected_score


def test_accessibility_score_combines_all_components():
    row = pd.Series(
        {
            "nearest_pharmacy_km": 0.5,
            "pharmacies_within_1km": 3,
            "pharmacies_within_5km": 10,
        }
    )

    assert calculate_accessibility_score(row) == 100


@pytest.mark.parametrize(
    ("score", "expected_category"),
    [
        (0, "LOW_ACCESS"),
        (39, "LOW_ACCESS"),
        (40, "LIMITED_ACCESS"),
        (59, "LIMITED_ACCESS"),
        (60, "MODERATE_ACCESS"),
        (79, "MODERATE_ACCESS"),
        (80, "HIGH_ACCESS"),
        (100, "HIGH_ACCESS"),
    ],
)
def test_classify_accessibility_boundaries(
    score,
    expected_category,
):
    assert classify_accessibility(score) == expected_category
