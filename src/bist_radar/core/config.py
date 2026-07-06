"""Application configuration."""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    """Application configuration."""

    app_name: str = "BIST Radar AI"
    version: str = "0.1.0"
    log_level: str = "INFO"
    database_name: str = "bist_radar.db"