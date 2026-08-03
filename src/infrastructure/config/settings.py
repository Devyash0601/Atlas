"""Environment-based typed infrastructure settings and configuration loader."""

import os
from typing import Literal


class Settings:
    """Base immutable infrastructure settings loaded from environment variables."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "ATLAS-EO")
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
        self.database_url: str = os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/atlas_db"
        )
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "artifacts")


class DevelopmentSettings(Settings):
    """Development environment settings."""

    def __init__(self) -> None:
        super().__init__()
        self.environment = "development"
        self.debug = True


class TestingSettings(Settings):
    """Testing environment settings."""

    __test__ = False

    def __init__(self) -> None:
        super().__init__()
        self.environment = "testing"
        self.debug = True
        self.database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/atlas_test_db"


class ProductionSettings(Settings):
    """Production environment settings."""

    def __init__(self) -> None:
        super().__init__()
        self.environment = "production"
        self.debug = False


class ConfigurationLoader:
    """Factory utility loading settings based on environment mode."""

    @staticmethod
    def load(env_name: Literal["development", "testing", "production"] | None = None) -> Settings:
        """Load settings for specified environment or environment variable."""
        env = env_name or os.getenv("ENVIRONMENT", "development").lower()
        if env == "production":
            return ProductionSettings()
        if env == "testing":
            return TestingSettings()
        return DevelopmentSettings()
