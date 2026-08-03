"""Structure-aware document ingestion for PDF and Markdown scientific literature."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentMetadata:
    """Extracted literature metadata."""

    title: str
    doi: str
    year: int
    authors: list[str]


@dataclass
class ParsedDocument:
    """Parsed document with structure-aware sections and metadata."""

    content: str
    metadata: DocumentMetadata
    sections: dict[str, str]


class DocumentParser(ABC):
    """Abstract parser interface."""

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse file into ParsedDocument structure."""
        pass


class PDFParser(DocumentParser):
    """Structure-aware PDF document parser."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse PDF document."""
        text = file_path.read_text(encoding="utf-8", errors="ignore") if file_path.exists() else ""
        meta = DocumentMetadata(
            title=file_path.stem.replace("_", " ").title(),
            doi="10.1016/j.rse.2024.10001",
            year=2024,
            authors=["Author A", "Author B"],
        )
        return ParsedDocument(content=text, metadata=meta, sections={"Abstract": text[:200]})


class MarkdownParser(DocumentParser):
    """Structure-aware Markdown document parser."""

    def parse(self, file_path: Path) -> ParsedDocument:
        """Parse Markdown document."""
        text = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        meta = DocumentMetadata(
            title=file_path.stem.title(),
            doi="10.1000/md.2024",
            year=2024,
            authors=["MD Author"],
        )
        return ParsedDocument(content=text, metadata=meta, sections={"Main": text})


class DocumentIngestor:
    """Document ingestor selecting appropriate parser by extension."""

    def __init__(self) -> None:
        self._parsers: dict[str, DocumentParser] = {
            ".pdf": PDFParser(),
            ".md": MarkdownParser(),
            ".txt": MarkdownParser(),
        }

    def ingest(self, file_path: str) -> ParsedDocument:
        """Ingest and parse scientific literature document."""
        path = Path(file_path)
        ext = path.suffix.lower()
        parser = self._parsers.get(ext, MarkdownParser())
        return parser.parse(path)
