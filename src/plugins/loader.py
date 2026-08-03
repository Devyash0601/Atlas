"""Plugin loader infrastructure and abstract provider extension contracts."""

from abc import ABC, abstractmethod
from typing import Any

from src.plugins.plugin import Plugin
from src.plugins.registry import registry
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class LLMPluginContract(Plugin, ABC):
    """Abstract contract interface for LLM provider plugins."""

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """Generate response from text prompt."""
        pass


class VisionPluginContract(Plugin, ABC):
    """Abstract contract interface for Vision model plugins."""

    @abstractmethod
    async def analyze_visual_data(self, image_path: str, **kwargs: Any) -> dict[str, Any]:
        """Analyze image or raster visualization."""
        pass


class EmbeddingPluginContract(Plugin, ABC):
    """Abstract contract interface for text embedding plugins."""

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate vector embeddings for input texts."""
        pass


class EarthEnginePluginContract(Plugin, ABC):
    """Abstract contract interface for Earth Engine workflow plugins."""

    @abstractmethod
    async def execute_spatial_query(
        self, aoi_geometry: dict[str, Any], date_range: tuple[str, str]
    ) -> dict[str, Any]:
        """Execute Earth Engine remote sensing workflow."""
        pass


class StoragePluginContract(Plugin, ABC):
    """Abstract contract interface for storage provider plugins."""

    @abstractmethod
    async def save_artifact(self, filename: str, content: bytes) -> str:
        """Save scientific report artifact or raster output."""
        pass


class PluginLoader:
    """Infrastructure service to dynamically discover and load plugin classes."""

    @staticmethod
    def register_plugin(plugin: Plugin) -> None:
        """Load and register a plugin instance."""
        registry.register(plugin)
        logger.info("Loaded plugin instance into framework", name=plugin.metadata.name)
