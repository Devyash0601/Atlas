"""Base Plugin definition and metadata interfaces for ATLAS-EO extensions."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PluginKind(StrEnum):
    """Categorization of supported ATLAS-EO plugin types."""

    LLM = "llm"
    VISION = "vision"
    EMBEDDING = "embedding"
    EARTH_ENGINE = "earth_engine"
    STORAGE = "storage"
    EVALUATION = "evaluation"
    PLANNER = "planner"
    RETRIEVER = "retriever"
    REPORT = "report"


class PluginMetadata(BaseModel):
    """Metadata describing a plugin implementation."""

    name: str = Field(description="Unique plugin name identifier")
    version: str = Field(description="Plugin semantic version")
    kind: PluginKind = Field(description="Plugin category type")
    description: str = Field(description="Human-readable description of plugin functionality")
    author: str = Field(default="ATLAS-EO Core Team", description="Plugin author")


class Plugin(ABC):
    """Abstract base class for all ATLAS-EO plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin metadata definition."""
        pass

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize plugin resources with runtime settings."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up and release plugin resources."""
        pass
