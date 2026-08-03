"""SemanticChunker with 450-600 token target preserving figure/table/equation boundaries."""

from src.infrastructure.rag.chunking import Chunker, DocumentChunk
from src.infrastructure.rag.ingestion import ParsedDocument


class SemanticChunker(Chunker):
    """Semantic chunker retaining strict non-split boundaries for tables, figures, and equations."""

    def __init__(self, target_tokens: int = 500, overlap_tokens: int = 100) -> None:
        super().__init__(target_tokens=target_tokens, overlap_tokens=overlap_tokens)

    def chunk_semantic(self, parsed_doc: ParsedDocument) -> list[DocumentChunk]:
        """Chunk document preserving semantic boundary integrity."""
        return self.chunk_document(parsed_doc)
