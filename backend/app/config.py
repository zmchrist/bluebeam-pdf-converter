"""
Configuration settings for Bluebeam PDF Map Converter.

Manages environment variables, file paths, and application settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine project root relative to this file
# This file is at: backend/app/config.py
# Backend root is at: backend/
# Project root is at: bluebeam-pdf-converter/
_THIS_FILE = Path(__file__).resolve()
_BACKEND_ROOT = _THIS_FILE.parent.parent  # backend/
_PROJECT_ROOT = _BACKEND_ROOT.parent  # bluebeam-pdf-converter/


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    app_name: str = "Bluebeam PDF Map Converter"
    version: str = "1.0.0"
    debug: bool = False

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]

    # File storage settings
    max_file_size_mb: int = 50
    file_retention_hours: int = 1
    temp_dir: Path = _BACKEND_ROOT / "data" / "temp"

    # Mapping configuration
    mapping_file: Path = _BACKEND_ROOT / "data" / "mapping.md"
    toolchest_dir: Path = _PROJECT_ROOT / "toolchest"
    bid_tools_dir: Path = _PROJECT_ROOT / "toolchest" / "bidTools"
    deployment_tools_dir: Path = _PROJECT_ROOT / "toolchest" / "deploymentTools"

    # Reference files
    samples_dir: Path = _PROJECT_ROOT / "samples"
    deployment_map_path: Path = _PROJECT_ROOT / "samples" / "maps" / "DeploymentMap.pdf"
    layer_reference_pdf: Path = _PROJECT_ROOT / "samples" / "EVENT26 IT Deployment [v0.0] [USE TO IMPORT LAYER FORMATTING].pdf"

    # Tuner settings
    icon_overrides_file: Path = _BACKEND_ROOT / "data" / "icon_overrides.json"
    gear_icons_dir: Path = _PROJECT_ROOT / "samples" / "icons" / "gearIcons"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Global settings instance
settings = Settings()
