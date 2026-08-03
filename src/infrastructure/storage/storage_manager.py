"""Storage managers for local, temporary, and artifact files."""

from abc import ABC, abstractmethod
from pathlib import Path


class LocalStorage(ABC):
    """Abstract local storage interface."""

    @abstractmethod
    async def write(self, path: str, data: bytes) -> None:
        """Write bytes to path."""
        pass

    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read bytes from path."""
        pass


class TemporaryStorage(LocalStorage):
    """In-memory or temp directory storage manager."""

    def __init__(self) -> None:
        self._memory: dict[str, bytes] = {}

    async def write(self, path: str, data: bytes) -> None:
        """Write to memory storage."""
        self._memory[path] = data

    async def read(self, path: str) -> bytes:
        """Read from memory storage."""
        if path not in self._memory:
            raise FileNotFoundError(f"Path '{path}' not found in temporary storage.")
        return self._memory[path]


class ArtifactStorage:
    """Artifact filesystem storage manager."""

    def __init__(self, base_dir: str = "artifacts") -> None:
        self.base_dir = Path(base_dir)

    def get_artifact_path(self, filename: str) -> Path:
        """Resolve full artifact file path."""
        return self.base_dir / filename


class StorageManager:
    """Storage manager aggregating temporary and artifact storage engines."""

    def __init__(self, base_dir: str = "artifacts") -> None:
        self.temp_storage = TemporaryStorage()
        self.artifact_storage = ArtifactStorage(base_dir)
