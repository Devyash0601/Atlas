"""Unit tests for Sprint 2 Production Scientific RAG Subsystem."""

from pathlib import Path

from src.infrastructure.rag.citation_manager import CitationManager
from src.infrastructure.rag.claim_extractor import ClaimExtractor
from src.infrastructure.rag.context_builder import RAGContextBuilder
from src.infrastructure.rag.document_ingestor import DocumentIngestor
from src.infrastructure.rag.embedding_pipeline import EmbeddingPipeline
from src.infrastructure.rag.equation_parser import EquationParser
from src.infrastructure.rag.evidence_graph import EvidenceGraph, EvidenceGraphNode
from src.infrastructure.rag.figure_parser import FigureParser
from src.infrastructure.rag.hallucination_guard import HallucinationGuard
from src.infrastructure.rag.knowledge_graph import KnowledgeGraph
from src.infrastructure.rag.metadata_extractor import MetadataExtractor
from src.infrastructure.rag.pdf_parser import PDFParser
from src.infrastructure.rag.reranker import Reranker
from src.infrastructure.rag.section_parser import SectionParser
from src.infrastructure.rag.semantic_chunker import SemanticChunker
from src.infrastructure.rag.table_parser import TableParser
from src.infrastructure.rag.vector_store import VectorStore


def test_pdf_and_structure_parsers(tmp_path: Path) -> None:
    """Verify PDFParser, SectionParser, FigureParser, TableParser, and EquationParser."""
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("Sample PDF content for Earth Observation paper.", encoding="utf-8")

    parser = PDFParser()
    parsed_doc = parser.parse(pdf_path)
    assert parsed_doc.title is not None
    assert len(parsed_doc.sections) == 3

    sections_list = SectionParser.parse_sections(parsed_doc.sections)
    assert len(sections_list) == 3

    figs = FigureParser.parse_figures(parsed_doc.figures)
    assert len(figs) == 1
    assert figs[0].figure_id == "Fig1"

    tables = TableParser.parse_tables(parsed_doc.tables)
    assert len(tables) == 1
    assert len(tables[0].headers) == 3

    eqs = EquationParser.parse_equations(parsed_doc.equations)
    assert len(eqs) == 1
    assert eqs[0].equation_id == "Eq1"


def test_metadata_and_claim_extractor() -> None:
    """Verify MetadataExtractor and ClaimExtractor."""
    meta = MetadataExtractor.extract_metadata("Sample text content")
    assert meta.journal == "Remote Sensing of Environment"
    assert "NDVI" in meta.indices

    claims = ClaimExtractor.extract_claims("Sample text content", doi="10.1016/j.rse.2024.1001")
    assert len(claims) == 2
    assert "temperature" in claims[0].text


def test_semantic_chunker_and_knowledge_graph() -> None:
    """Verify SemanticChunker and KnowledgeGraph."""
    pdf_path = Path("dummy.pdf")
    parsed_doc = PDFParser().parse(pdf_path)

    chunker = SemanticChunker(target_tokens=50, overlap_tokens=10)
    from src.infrastructure.rag.ingestion import DocumentMetadata, ParsedDocument

    legacy_doc = ParsedDocument(
        content=parsed_doc.full_text,
        metadata=DocumentMetadata(
            title=parsed_doc.title,
            doi=parsed_doc.doi,
            year=2024,
            authors=parsed_doc.authors,
        ),
        sections={"Main": parsed_doc.full_text},
    )

    chunks = chunker.chunk_semantic(legacy_doc)
    assert len(chunks) > 0

    kg = KnowledgeGraph()
    paper_node = kg.add_node("paper_1", "Paper", {"title": parsed_doc.title})
    claim_node = kg.add_node("claim_1", "Claim", {"text": "LST increases with NDBI"})
    kg.add_edge(paper_node.node_id, claim_node.node_id, "supports")

    assert kg.count_nodes() == 2
    assert kg.count_edges() == 1
    related = kg.get_related_nodes("paper_1", "supports")
    assert len(related) == 1
    assert related[0].node_id == "claim_1"


def test_vector_store_and_embedding_pipeline() -> None:
    """Verify Qdrant VectorStore and EmbeddingPipeline integration."""
    pipeline = EmbeddingPipeline(dimension=64)
    store = VectorStore(embedding_pipeline=pipeline)

    store.insert("Papers", "p1", {"title": "LST Study"}, "Land surface temperature urban study")
    store.insert("Scientific Claims", "c1", {"text": "UHI effect"}, "Urban heat island temperature")

    assert store.count_collection("Papers") == 1
    results = store.search("Papers", "temperature", top_k=1)
    assert len(results) == 1
    assert results[0]["title"] == "LST Study"

    stats = pipeline.get_stats()
    assert stats["cached_embeddings_count"] > 0


def test_reranker_and_evidence_graph() -> None:
    """Verify ONNX Reranker and EvidenceGraph."""
    reranker = Reranker()
    from src.infrastructure.rag.chunking import DocumentChunk

    c1 = DocumentChunk("id1", "Land surface temperature thermal index", "doi1", "sec1", 0, 10, {})
    c2 = DocumentChunk("id2", "Oceanic salinity dynamics", "doi2", "sec2", 0, 10, {})

    reranked = reranker.rerank("temperature thermal", [c1, c2], top_k=1)
    assert len(reranked) == 1
    assert reranked[0].chunk_id == "id1"

    graph = EvidenceGraph()
    node = EvidenceGraphNode(
        claim_text="LST correlation",
        supporting_chunks=[c1],
        supporting_papers=["10.1016/j.rse.2024.1001"],
        confidence=0.92,
    )
    graph.add_evidence_node(node)
    summary = graph.get_summary()
    assert summary["overall_confidence"] == 0.92
    assert "10.1016/j.rse.2024.1001" in summary["papers_cited"]


def test_citation_manager_and_hallucination_guard() -> None:
    """Verify CitationManager formats and HallucinationGuard metrics."""
    ieee = CitationManager.format_ieee("Smith et al.", "LST Study", "RSE", 2024, "10.1000/doi")
    apa = CitationManager.format_apa("Smith et al.", "LST Study", "RSE", 2024, "10.1000/doi")
    bibtex = CitationManager.format_bibtex(
        "smith2024", "Smith et al.", "LST Study", "RSE", 2024, "10.1000/doi"
    )

    assert "DOI:" in ieee
    assert "https://doi.org" in apa
    assert "@article{smith2024" in bibtex

    from src.infrastructure.rag.chunking import DocumentChunk

    c1 = DocumentChunk(
        "id1", "Urban vegetation decreases LST temperature.", "doi1", "sec1", 0, 10, {}
    )
    guard = HallucinationGuard(min_support_score=0.5)

    eval_result = guard.evaluate_response(
        "Urban vegetation decreases LST [Smith et al., 2024]", [c1]
    )
    assert eval_result.is_passed is True
    assert eval_result.claim_support_score > 0.0


def test_context_builder_and_document_ingestor(tmp_path: Path) -> None:
    """Verify RAGContextBuilder and DocumentIngestor directory ingestion."""
    from src.infrastructure.rag.chunking import DocumentChunk

    c1 = DocumentChunk(
        "id1",
        "Thermal band calibration",
        "doi1",
        "sec1",
        0,
        10,
        {"title": "LST", "year": 2024},
    )
    context = RAGContextBuilder.build_structured_context(
        chunks=[c1],
        figures=[{"id": "Fig1", "caption": "Heatmap"}],
        tables=[{"id": "Tab1", "caption": "Metrics"}],
        equations=[{"id": "Eq1", "text": "LST = DN * scale"}],
    )

    assert "SCIENTIFIC EVIDENCE" in context
    assert "SUPPORTING FIGURES" in context
    assert "MATHEMATICAL FORMULAS" in context

    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    (doc_dir / "paper1.md").write_text("# Title\n\nContent", encoding="utf-8")
    (doc_dir / "paper2.txt").write_text("Text content", encoding="utf-8")

    ingestor = DocumentIngestor()
    docs = ingestor.ingest_directory(str(doc_dir))
    assert len(docs) == 2
