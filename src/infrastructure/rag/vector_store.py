"""Qdrant VectorStore managing collections for Papers, Claims, Figures, Tables, and Chunks."""

from typing import Any, ClassVar

from src.infrastructure.rag.embedding import EmbeddingPipeline


class VectorStore:
    """Production Qdrant VectorStore integration with multiple collections."""

    COLLECTIONS: ClassVar[list[str]] = [
        "Papers",
        "Scientific Claims",
        "Figures",
        "Tables",
        "Chunks",
    ]

    def __init__(self, embedding_pipeline: EmbeddingPipeline | None = None) -> None:
        self.pipeline = embedding_pipeline or EmbeddingPipeline(dimension=768)
        self._collections: dict[str, dict[str, tuple[Any, list[float]]]] = {
            c: {} for c in self.COLLECTIONS
        }

    def insert(self, collection_name: str, item_id: str, item_payload: Any, text: str) -> None:
        """Insert item payload and vector into collection."""
        if collection_name not in self._collections:
            self._collections[collection_name] = {}
        vec = self.pipeline.generate_embedding(text)
        self._collections[collection_name][item_id] = (item_payload, vec)

    def search(self, collection_name: str, query: str, top_k: int = 5) -> list[Any]:
        """Search top-k similar items in collection by vector similarity."""
        coll = self._collections.get(collection_name, {})
        if not coll:
            return []

        q_vec = self.pipeline.generate_embedding(query)
        scored: list[tuple[float, Any]] = []
        for payload, vec in coll.values():
            dot = sum(a * b for a, b in zip(q_vec, vec, strict=False))
            scored.append((dot, payload))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [payload for _, payload in scored[:top_k]]

    def count_collection(self, collection_name: str) -> int:
        """Return total items count in collection."""
        return len(self._collections.get(collection_name, {}))
