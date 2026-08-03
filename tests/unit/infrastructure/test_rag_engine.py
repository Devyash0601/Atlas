"""Unit tests for Scientific RAG Engine."""

from pathlib import Path

from src.infrastructure.rag.chunking import Chunker
from src.infrastructure.rag.citation import (
    CitationResolver,
    EvidenceCollector,
    HallucinationGuard,
    QueryPlanner,
    ReferenceFormatter,
)
from src.infrastructure.rag.embedding import EmbeddingPipeline
from src.infrastructure.rag.indexer import VectorIndexer
from src.infrastructure.rag.ingestion import DocumentIngestor, MarkdownParser, PDFParser
from src.infrastructure.rag.retriever import HybridRetriever


def test_document_ingestion(tmp_path: Path) -> None:
    """Verify document ingestion and parsers."""
    doc_file = tmp_path / "paper.md"
    doc_file.write_text("# Remote Sensing Study\n\nNDVI analysis for Paris.", encoding="utf-8")

    ingestor = DocumentIngestor()
    parsed = ingestor.ingest(str(doc_file))
    assert "Remote Sensing" in parsed.content
    assert parsed.metadata.year == 2024

    pdf_parser = PDFParser()
    parsed_pdf = pdf_parser.parse(tmp_path / "test.pdf")
    assert parsed_pdf.metadata.doi is not None


def test_chunker_and_vector_indexer() -> None:
    """Verify Chunker and VectorIndexer."""
    doc_file = Path("dummy.md")
    parsed = MarkdownParser().parse(doc_file)
    parsed.content = "Word " * 200

    chunker = Chunker(target_tokens=50, overlap_tokens=10)
    chunks = chunker.chunk_document(parsed)
    assert len(chunks) > 0

    pipeline = EmbeddingPipeline(dimension=64)
    indexer = VectorIndexer(pipeline)
    indexer.index_chunks(chunks)
    assert indexer.count() == len(chunks)

    results = indexer.search_similar("Word", top_k=2)
    assert len(results) <= 2


def test_hybrid_retriever_and_reranker() -> None:
    """Verify HybridRetriever and Reranker."""
    doc_file = Path("paper.md")
    parsed = MarkdownParser().parse(doc_file)
    parsed.content = "Thermal land surface temperature study in urban heat island."

    chunker = Chunker(target_tokens=50, overlap_tokens=10)
    chunks = chunker.chunk_document(parsed)

    pipeline = EmbeddingPipeline(dimension=64)
    indexer = VectorIndexer(pipeline)
    indexer.index_chunks(chunks)

    retriever = HybridRetriever(indexer)
    retrieved = retriever.retrieve("thermal surface temperature", top_k=2)
    assert len(retrieved) > 0


def test_citation_and_hallucination_guard() -> None:
    """Verify CitationResolver, EvidenceCollector, and HallucinationGuard."""
    parsed = MarkdownParser().parse(Path("ref.md"))
    parsed.content = "Urban vegetation decreases LST temperature by 3 degrees Celsius."

    chunker = Chunker(target_tokens=50, overlap_tokens=10)
    chunks = chunker.chunk_document(parsed)

    citation = CitationResolver.resolve_citation(chunks[0])
    assert "2024" in citation

    ref_str = ReferenceFormatter.format_reference(chunks[0].doi, "UHI Study", 2024)
    assert "DOI:" in ref_str

    collector = EvidenceCollector()
    ev = collector.collect(chunks[0], "LST reduction", 0.95)
    assert ev.confidence == 0.95

    # Hallucination guard check
    supported = HallucinationGuard.verify_claim_support("Urban vegetation LST temperature", chunks)
    assert supported is True

    unsupported = HallucinationGuard.verify_claim_support("Unrelated oceanography claim", chunks)
    assert unsupported is False

    subqueries = QueryPlanner.plan_subqueries("UHI Paris")
    assert len(subqueries) == 3
