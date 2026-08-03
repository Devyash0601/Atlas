"""Abstract provider infrastructure adapters contracts."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProviderAdapter(ABC):
    """Abstract infrastructure adapter for LLM inference engines."""

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text completion from prompt."""
        pass


class EmbeddingProviderAdapter(ABC):
    """Abstract infrastructure adapter for vector embedding models."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate vector embedding array for text input."""
        pass


class VisionProviderAdapter(ABC):
    """Abstract infrastructure adapter for Vision-Language Models."""

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """Analyze image input using vision model."""
        pass


class EarthEngineProviderAdapter(ABC):
    """Abstract infrastructure adapter for Earth Engine geospatial computation."""

    @abstractmethod
    async def compute_index(
        self, index_name: str, bounds: tuple[float, float, float, float]
    ) -> dict[str, Any]:
        """Execute raster index computation over bounding box."""
        pass


class StorageProviderAdapter(ABC):
    """Abstract infrastructure adapter for blob storage operations."""

    @abstractmethod
    async def save_file(self, relative_path: str, content: bytes) -> str:
        """Save file content bytes and return stored path."""
        pass

    @abstractmethod
    async def read_file(self, relative_path: str) -> bytes:
        """Read file bytes from relative path."""
        pass


class NotificationProviderAdapter(ABC):
    """Abstract infrastructure adapter for notifications."""

    @abstractmethod
    async def send_notification(self, recipient: str, message: str) -> bool:
        """Send notification message to recipient."""
        pass


class AuthenticationProviderAdapter(ABC):
    """Abstract infrastructure adapter for authentication identity verification."""

    @abstractmethod
    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify auth token payload."""
        pass
