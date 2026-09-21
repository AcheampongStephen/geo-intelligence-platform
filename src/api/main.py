import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException

from src.api.exception_handlers import dataset_not_found_handler
from src.api.exceptions import DatasetNotFoundError
from src.config.logging import configure_logging
from src.config.settings import settings

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    logger.info(
        "Starting %s version=%s environment=%s",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    yield

    logger.info(
        "Shutting down %s",
        settings.app_name,
    )


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API providing hospital, pharmacy accessibility, "
        "and geospatial intelligence derived from "
        "OpenStreetMap data."
    ),
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------

app.add_exception_handler(
    DatasetNotFoundError,
    dataset_not_found_handler,
)


# ---------------------------------------------------------
# Data functions
# ---------------------------------------------------------


def load_metrics() -> pd.DataFrame:
    """
    Load the curated hospital-pharmacy intelligence dataset.
    """

    if not settings.metrics_path.exists():
        raise DatasetNotFoundError(str(settings.metrics_path))

    logger.debug(
        "Loading metrics dataset from %s",
        settings.metrics_path,
    )

    data = pd.read_parquet(settings.metrics_path)

    logger.debug(
        "Loaded %d hospital records",
        len(data),
    )

    return data


def dataframe_to_records(
    data: pd.DataFrame,
) -> list[dict]:
    """
    Convert a pandas DataFrame into JSON-safe records.

    Pandas represents missing values using NaN/NaT.
    JSON uses null, so missing values are converted
    into None before serialization.
    """

    cleaned = data.astype(object).where(
        pd.notna(data),
        None,
    )

    return cleaned.to_dict(orient="records")


def get_hospital_record(
    data: pd.DataFrame,
    hospital_id: int,
) -> pd.DataFrame:
    """
    Return the hospital matching the supplied
    OpenStreetMap ID.
    """

    result = data[data["hospital_osm_id"] == hospital_id]

    if result.empty:
        logger.warning(
            "Hospital not found: hospital_id=%s",
            hospital_id,
        )

        raise HTTPException(
            status_code=404,
            detail=(f"Hospital {hospital_id} not found."),
        )

    return result


# ---------------------------------------------------------
# System endpoints
# ---------------------------------------------------------


@app.get(
    "/",
    tags=["system"],
    summary="API information",
)
def root():
    """
    Return basic information about the API.
    """

    return {
        "service": settings.app_name,
        "status": "online",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
)
def health_check():
    """
    Check whether the application and required
    intelligence dataset are available.
    """

    dataset_exists = settings.metrics_path.exists()

    if dataset_exists:
        logger.debug("Health check successful.")
    else:
        logger.error("Health check degraded: metrics dataset missing.")

    return {
        "status": ("healthy" if dataset_exists else "degraded"),
        "environment": (settings.environment),
        "dataset": str(settings.metrics_path),
        "dataset_exists": (dataset_exists),
    }


# ---------------------------------------------------------
# Hospital endpoints
# ---------------------------------------------------------


@app.get(
    "/hospitals",
    tags=["hospitals"],
    summary="Get all hospitals",
)
def get_hospitals():
    """
    Return all hospitals and their
    accessibility intelligence.
    """

    data = load_metrics()

    records = dataframe_to_records(data)

    logger.info(
        "Hospital collection requested: count=%d",
        len(records),
    )

    return {
        "count": len(records),
        "hospitals": records,
    }


@app.get(
    "/hospitals/{hospital_id}",
    tags=["hospitals"],
    summary="Get a hospital by OSM ID",
)
def get_hospital(
    hospital_id: int,
):
    """
    Return a hospital using its
    OpenStreetMap identifier.
    """

    data = load_metrics()

    result = get_hospital_record(
        data,
        hospital_id,
    )

    records = dataframe_to_records(result)

    logger.info(
        "Hospital requested: hospital_id=%s",
        hospital_id,
    )

    return records[0]


# ---------------------------------------------------------
# Pharmacy accessibility endpoint
# ---------------------------------------------------------


@app.get(
    "/hospitals/{hospital_id}/pharmacy-access",
    tags=["pharmacy-access"],
    summary=("Get pharmacy accessibility for a hospital"),
)
def get_pharmacy_access(
    hospital_id: int,
):
    """
    Return pharmacy accessibility intelligence
    for a specific hospital.
    """

    data = load_metrics()

    result = get_hospital_record(
        data,
        hospital_id,
    )

    row = result.iloc[0]

    logger.info(
        "Pharmacy accessibility requested: hospital_id=%s",
        hospital_id,
    )

    return {
        "hospital_osm_id": int(row["hospital_osm_id"]),
        "hospital_name": (
            None if pd.isna(row["hospital_name"]) else row["hospital_name"]
        ),
        "nearest_pharmacy": (
            None if pd.isna(row["nearest_pharmacy"]) else row["nearest_pharmacy"]
        ),
        "nearest_pharmacy_osm_id": (
            None
            if pd.isna(row["nearest_pharmacy_osm_id"])
            else int(row["nearest_pharmacy_osm_id"])
        ),
        "nearest_pharmacy_km": (
            None
            if pd.isna(row["nearest_pharmacy_km"])
            else float(row["nearest_pharmacy_km"])
        ),
        "nearest_pharmacy_category": (
            None
            if pd.isna(row["nearest_pharmacy_category"])
            else row["nearest_pharmacy_category"]
        ),
        "pharmacies_within_1km": int(row["pharmacies_within_1km"]),
        "pharmacies_within_2km": int(row["pharmacies_within_2km"]),
        "pharmacies_within_5km": int(row["pharmacies_within_5km"]),
        "coverage_1km": bool(row["coverage_1km"]),
        "coverage_2km": bool(row["coverage_2km"]),
        "coverage_5km": bool(row["coverage_5km"]),
        "accessibility_score": float(row["accessibility_score"]),
        "accessibility_category": (row["accessibility_category"]),
        "nearest_pharmacy_name_available": bool(row["nearest_pharmacy_name_available"]),
        "has_pharmacy_within_5km": bool(row["has_pharmacy_within_5km"]),
    }


# ---------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------


@app.get(
    "/analytics/summary",
    tags=["analytics"],
    summary="Get platform analytics summary",
)
def get_summary():
    """
    Return summary statistics for
    hospital-pharmacy accessibility.
    """

    data = load_metrics()

    accessibility_categories = data["accessibility_category"].value_counts().to_dict()

    logger.info("Analytics summary requested.")

    return {
        "total_hospitals": len(data),
        "hospitals_with_pharmacy_within_1km": int(data["coverage_1km"].sum()),
        "hospitals_with_pharmacy_within_2km": int(data["coverage_2km"].sum()),
        "hospitals_with_pharmacy_within_5km": int(data["coverage_5km"].sum()),
        "average_nearest_pharmacy_km": round(
            float(data["nearest_pharmacy_km"].mean()),
            2,
        ),
        "maximum_nearest_pharmacy_km": round(
            float(data["nearest_pharmacy_km"].max()),
            2,
        ),
        "accessibility_categories": (accessibility_categories),
    }
