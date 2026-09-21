from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app
from src.config.settings import settings

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "Geo-Intelligence Platform API"
    assert data["status"] == "online"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["dataset_exists"] is True


def test_get_hospitals():
    response = client.get("/hospitals")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 14
    assert len(data["hospitals"]) == 14


def test_hospitals_are_json_safe():
    response = client.get("/hospitals")

    assert response.status_code == 200

    data = response.json()

    for hospital in data["hospitals"]:
        for value in hospital.values():
            assert value is None or not pd.isna(value)


def test_get_hospital():
    hospital_id = 10834291446

    response = client.get(f"/hospitals/{hospital_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["hospital_osm_id"] == hospital_id
    assert data["hospital_name"] == ("Midlands Regional Rehabilitation Hospital")


def test_get_nonexistent_hospital():
    response = client.get("/hospitals/999999999999")

    assert response.status_code == 404


def test_pharmacy_access():
    hospital_id = 10834291446

    response = client.get(f"/hospitals/{hospital_id}/pharmacy-access")

    assert response.status_code == 200

    data = response.json()

    assert data["hospital_osm_id"] == hospital_id

    assert data["nearest_pharmacy_km"] is not None

    assert data["nearest_pharmacy_km"] > 10

    assert data["pharmacies_within_1km"] == 0

    assert data["pharmacies_within_2km"] == 0

    assert data["pharmacies_within_5km"] == 0

    assert data["has_pharmacy_within_5km"] is False


def test_analytics_summary():
    response = client.get("/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_hospitals"] == 14

    assert data["hospitals_with_pharmacy_within_1km"] == 7

    assert data["hospitals_with_pharmacy_within_2km"] == 9

    assert data["hospitals_with_pharmacy_within_5km"] == 13

    assert data["average_nearest_pharmacy_km"] == 2.21

    assert data["maximum_nearest_pharmacy_km"] == 11.05


def test_missing_dataset_returns_500(monkeypatch):
    """
    API should return a controlled 500 response when
    the required metrics dataset does not exist.
    """

    fake_path = Path("data/curated/this_dataset_does_not_exist.parquet")

    monkeypatch.setattr(
        settings,
        "metrics_path",
        fake_path,
    )

    response = client.get("/analytics/summary")

    assert response.status_code == 500

    assert response.json() == {
        "error": "dataset_unavailable",
        "message": ("Required platform data is unavailable."),
    }


def test_missing_dataset_does_not_expose_path(
    monkeypatch,
):
    """
    API error responses must not expose internal
    filesystem paths.
    """

    fake_path = Path("C:/private/internal/secret_metrics.parquet")

    monkeypatch.setattr(
        settings,
        "metrics_path",
        fake_path,
    )

    response = client.get("/hospitals")

    response_body = response.text

    assert response.status_code == 500

    assert "secret_metrics.parquet" not in response_body
    assert "C:/private/internal" not in response_body


def test_health_degraded_when_dataset_missing(monkeypatch):
    fake_path = Path("data/curated/health_check_missing.parquet")

    monkeypatch.setattr(
        settings,
        "metrics_path",
        fake_path,
    )

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "degraded"
    assert data["dataset_exists"] is False
