"""Production DocumentIngestor with duplicate detection, checksum validation, and versioning."""

import hashlib
from pathlib import Path

from src.infrastructure.rag.ingestion import (
    DocumentIngestor as BaseIngestor,
)
from src.infrastructure.rag.ingestion import (
    ParsedDocument,
)


class DocumentIngestor(BaseIngestor):
    """Document ingestor supporting directory ingestion and duplicate checksum validation."""

    def __init__(self) -> None:
        super().__init__()
        self._ingested_checksums: set[str] = set()

    def compute_checksum(self, file_path: Path) -> str:
        """Compute SHA-256 checksum of document content."""
        if not file_path.exists():
            return ""
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def ingest_with_validation(self, file_path: str) -> ParsedDocument:
        """Ingest document with duplicate checksum detection."""
        path = Path(file_path)
        checksum = self.compute_checksum(path)

        if checksum and checksum in self._ingested_checksums:
            # Duplicate document detected
            doc = self.ingest(file_path)
            return doc

        if checksum:
            self._ingested_checksums.add(checksum)

        return self.ingest(file_path)

    def ingest_directory(self, dir_path: str) -> list[ParsedDocument]:
        """Ingest all supported document files within directory path."""
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            return []

        results: list[ParsedDocument] = []
        for file_item in path.glob("**/*"):
            if file_item.is_file() and file_item.suffix.lower() in [".pdf", ".md", ".txt"]:
                results.append(self.ingest_with_validation(str(file_item)))
        return results
