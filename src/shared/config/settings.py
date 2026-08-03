"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings derived from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Configuration
    ENVIRONMENT: Literal["development", "staging", "production", "testing"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    PROJECT_NAME: str = "ATLAS-EO"
    VERSION: str = "1.0.0"

    # PostgreSQL Database Settings
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "atlaseo"
    POSTGRES_USER: str = "atlas"
    POSTGRES_PASSWORD: str = "atlas_secret_pass"

    # Redis Cache & Session Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Qdrant Vector Store Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Ollama LLM Service Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_LLM_MODEL: str = "qwen3:8b"
    DEFAULT_EMBEDDING_MODEL: str = "nomic-embed-text"

    @property
    def postgres_dsn(self) -> str:
        """Asynchronous PostgreSQL DSN URI."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached global settings instance."""
    return Settings()
