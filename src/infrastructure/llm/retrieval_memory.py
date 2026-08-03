"""Retrieval memory storing literature chunks, citations, and confidence scores."""

from typing import Any

from src.infrastructure.llm.exceptions import MemoryError


class RetrievalMemory:
    """Retrieval memory storing literature chunks, citations, and confidence metrics."""

    def __init__(self) -> None:
        self._chunks: dict[str, dict[str, Any]] = {}

    def add(self, chunk_id: str, text: str, citation: str, confidence: float) -> None:
        """Store retrieved document chunk metadata."""
        if not chunk_id or not text:
            raise MemoryError("Retrieval chunk_id and text must not be empty.")
        self._chunks[chunk_id] = {
            "text": text,
            "citation": citation,
            "confidence": confidence,
        }

    def remove(self, chunk_id: str) -> None:
        """Remove chunk from retrieval memory."""
        if chunk_id not in self._chunks:
            raise MemoryError(f"Chunk '{chunk_id}' not found.")
        del self._chunks[chunk_id]

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search retrieved chunks by query string."""
        q = query.lower()
        return [
            {"chunk_id": k, **v}
            for k, v in self._chunks.items()
            if q in v["text"].lower() or q in v["citation"].lower()
        ]

    def get_citations(self) -> list[str]:
        """Return list of all unique citation keys."""
        return list({v["citation"] for v in self._chunks.values()})

    def summarize(self) -> str:
        """Summarize stored retrieval chunks."""
        return f"Retrieval memory stores {len(self._chunks)} document chunks."

    def clear(self) -> None:
        """Clear retrieval memory."""
        self._chunks.clear()

    def serialize(self) -> dict[str, Any]:
        """Serialize retrieval memory to dict."""
        return {"chunks": dict(self._chunks)}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "RetrievalMemory":
        """Deserialize dictionary into RetrievalMemory instance."""
        mem = cls()
        mem._chunks = dict(data.get("chunks", {}))
        return mem
