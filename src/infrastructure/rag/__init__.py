"""Production Scientific RAG Engine package."""

from src.infrastructure.rag.chunking import Chunker, DocumentChunk
from src.infrastructure.rag.citation import (
    CitationResolver,
    EvidenceCollector,
    EvidenceItem,
    QueryPlanner,
    ReferenceFormatter,
)
from src.infrastructure.rag.citation_manager import CitationManager
from src.infrastructure.rag.claim_extractor import ClaimExtractor, ScientificClaim
from src.infrastructure.rag.context_builder import RAGContextBuilder
from src.infrastructure.rag.document_ingestor import DocumentIngestor
from src.infrastructure.rag.embedding_pipeline import EmbeddingPipeline
from src.infrastructure.rag.equation_parser import EquationParser, ParsedEquation
from src.infrastructure.rag.evidence_graph import EvidenceGraph, EvidenceGraphNode
from src.infrastructure.rag.figure_parser import FigureParser, ParsedFigure
from src.infrastructure.rag.hallucination_guard import (
    HallucinationEvaluation,
    HallucinationGuard,
)
from src.infrastructure.rag.indexer import VectorIndexer
from src.infrastructure.rag.ingestion import (
    DocumentMetadata,
    MarkdownParser,
    ParsedDocument,
    PDFParser,
)
from src.infrastructure.rag.knowledge_graph import GraphEdge, GraphNode, KnowledgeGraph
from src.infrastructure.rag.metadata_extractor import MetadataExtractor, PaperMetadataPayload
from src.infrastructure.rag.pdf_parser import ParsedPDFDocument, ParsedSection
from src.infrastructure.rag.reranker import Reranker
from src.infrastructure.rag.retriever import HybridRetriever
from src.infrastructure.rag.section_parser import SectionParser
from src.infrastructure.rag.semantic_chunker import SemanticChunker
from src.infrastructure.rag.table_parser import ParsedTable, TableParser
from src.infrastructure.rag.vector_store import VectorStore

__all__ = [
    "Chunker",
    "CitationManager",
    "CitationResolver",
    "ClaimExtractor",
    "DocumentChunk",
    "DocumentIngestor",
    "DocumentMetadata",
    "EmbeddingPipeline",
    "EquationParser",
    "EvidenceCollector",
    "EvidenceGraph",
    "EvidenceGraphNode",
    "EvidenceItem",
    "FigureParser",
    "GraphEdge",
    "GraphNode",
    "HallucinationEvaluation",
    "HallucinationGuard",
    "HybridRetriever",
    "KnowledgeGraph",
    "MarkdownParser",
    "MetadataExtractor",
    "PDFParser",
    "PaperMetadataPayload",
    "ParsedDocument",
    "ParsedEquation",
    "ParsedFigure",
    "ParsedPDFDocument",
    "ParsedSection",
    "ParsedTable",
    "QueryPlanner",
    "RAGContextBuilder",
    "ReferenceFormatter",
    "Reranker",
    "ScientificClaim",
    "SectionParser",
    "SemanticChunker",
    "TableParser",
    "VectorIndexer",
    "VectorStore",
]
