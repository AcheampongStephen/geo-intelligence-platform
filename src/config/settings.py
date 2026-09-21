from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Geo-Intelligence Platform API"
    app_version: str = "1.0.0"
    environment: str = "development"

    log_level: str = "INFO"

    data_dir: Path = Path("data")
    metrics_path: Path = Path("data/curated/hospital_pharmacy_metrics.parquet")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
