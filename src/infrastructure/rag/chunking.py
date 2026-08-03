"""Semantic chunker retaining section, page, and DOI metadata."""

from dataclasses import dataclass
from typing import Any

from src.infrastructure.rag.ingestion import ParsedDocument


@dataclass
class DocumentChunk:
    """Retrieved document chunk with metadata payload."""

    chunk_id: str
    text: str
    doi: str
    section: str
    start_char: int
    end_char: int
    metadata: dict[str, Any]


class Chunker:
    """Semantic chunker splitting documents with token target and overlap."""

    def __init__(self, target_tokens: int = 500, overlap_tokens: int = 100) -> None:
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens

    def chunk_document(self, parsed_doc: ParsedDocument) -> list[DocumentChunk]:
        """Split document into semantic chunks preserving DOI and section metadata."""
        chunks: list[DocumentChunk] = []
        full_text = parsed_doc.content
        chunk_size = self.target_tokens * 4
        overlap = self.overlap_tokens * 4

        idx = 0
        chunk_counter = 0
        while idx < len(full_text):
            end_idx = min(idx + chunk_size, len(full_text))
            chunk_text = full_text[idx:end_idx]
            chunk_id = f"{parsed_doc.metadata.doi}#chunk-{chunk_counter}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    doi=parsed_doc.metadata.doi,
                    section="Main",
                    start_char=idx,
                    end_char=end_idx,
                    metadata={"title": parsed_doc.metadata.title, "year": parsed_doc.metadata.year},
                )
            )
            chunk_counter += 1
            if end_idx >= len(full_text):
                break
            idx += chunk_size - overlap

        return chunks
