"""Vector database indexer abstractions."""

from src.infrastructure.rag.chunking import DocumentChunk
from src.infrastructure.rag.embedding import EmbeddingPipeline


class VectorIndexer:
    """Vector database indexer storing chunks and embeddings."""

    def __init__(self, embedding_pipeline: EmbeddingPipeline) -> None:
        self.pipeline = embedding_pipeline
        self._index: dict[str, tuple[DocumentChunk, list[float]]] = {}

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Index chunks with embeddings."""
        for chunk in chunks:
            vec = self.pipeline.generate_embedding(chunk.text)
            self._index[chunk.chunk_id] = (chunk, vec)

    def count(self) -> int:
        """Return total indexed chunks count."""
        return len(self._index)

    def search_similar(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        """Search top-k similar chunks by vector cosine similarity."""
        if not self._index:
            return []
        q_vec = self.pipeline.generate_embedding(query)

        scored: list[tuple[float, DocumentChunk]] = []
        for chunk, vec in self._index.values():
            dot = sum(a * b for a, b in zip(q_vec, vec, strict=False))
            scored.append((dot, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
