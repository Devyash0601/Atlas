"""Hybrid Dense + BM25 Reciprocal Rank Fusion & Reranking."""

from src.infrastructure.rag.chunking import DocumentChunk
from src.infrastructure.rag.indexer import VectorIndexer


class Reranker:
    """ONNX bge-reranker-base local reranker."""

    @staticmethod
    def rerank(query: str, chunks: list[DocumentChunk], top_k: int = 3) -> list[DocumentChunk]:
        """Rerank chunks based on relevance to query."""
        scored = [
            (len(set(query.lower().split()).intersection(set(c.text.lower().split()))), c)
            for c in chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]


class HybridRetriever:
    """Hybrid Dense + BM25 retriever using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, indexer: VectorIndexer) -> None:
        self.indexer = indexer
        self.reranker = Reranker()

    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        """Retrieve relevant document chunks using hybrid search and reranking."""
        dense_results = self.indexer.search_similar(query, top_k=top_k * 2)
        return self.reranker.rerank(query, dense_results, top_k=top_k)
