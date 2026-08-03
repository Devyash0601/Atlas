"""Dependency injection container scaffold for FastAPI dependencies."""

import time
from typing import Annotated

from fastapi import Depends

from src.shared.config.settings import Settings, get_settings

START_TIME = time.time()


def get_start_time() -> float:
    """Return process start timestamp for uptime calculation."""
    return START_TIME


def get_app_settings() -> Settings:
    """Dependency provider for global application settings."""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
