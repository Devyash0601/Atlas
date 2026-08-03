"""Filesystem managers, path resolvers, and safe file writers."""

import tempfile
from pathlib import Path


class PathResolver:
    """Path resolver for absolute and relative paths."""

    @staticmethod
    def resolve(path_str: str) -> Path:
        """Resolve path string to absolute Path."""
        return Path(path_str).expanduser().resolve()


class TemporaryDirectoryManager:
    """Temporary directory manager."""

    def __init__(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory()

    @property
    def path(self) -> Path:
        """Return temporary directory path."""
        return Path(self._temp_dir.name)

    def cleanup(self) -> None:
        """Clean up temporary directory."""
        self._temp_dir.cleanup()


class ArtifactPathManager:
    """Manager resolving artifact output storage directory structure."""

    def __init__(self, root_dir: str = "artifacts") -> None:
        self.root_dir = PathResolver.resolve(root_dir)

    def get_path_for_workflow(self, workflow_id: str, filename: str) -> Path:
        """Return nested artifact path for workflow."""
        return self.root_dir / workflow_id / filename


class SafeFileWriter:
    """Atomic safe file writer preventing partial write corruption."""

    @staticmethod
    def write_text(target_path: Path, content: str) -> None:
        """Atomically write text content to target path."""
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(target_path)


class FileManager:
    """Filesystem file manager manager aggregating path resolution and safe operations."""

    def __init__(self, root_dir: str = "artifacts") -> None:
        self.artifact_paths = ArtifactPathManager(root_dir)
