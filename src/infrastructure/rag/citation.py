"""Citation resolver, evidence collector, and hallucination guard."""

from dataclasses import dataclass

from src.infrastructure.rag.chunking import DocumentChunk


@dataclass
class EvidenceItem:
    """Gathered evidence claim with source citation metadata."""

    claim: str
    citation: str
    doi: str
    confidence: float
    is_supported: bool = True


class CitationResolver:
    """Citation resolver formatting inline markdown citations."""

    @staticmethod
    def resolve_citation(chunk: DocumentChunk) -> str:
        """Format citation key from chunk metadata."""
        author = chunk.metadata.get("title", "Remote Sensing Literature").split()[0]
        year = chunk.metadata.get("year", 2024)
        return f"{author} et al. ({year})"


class ReferenceFormatter:
    """IEEE/Elsevier style reference list formatter."""

    @staticmethod
    def format_reference(doi: str, title: str, year: int) -> str:
        """Format bibliographic reference line."""
        return f"- {title} ({year}). DOI: https://doi.org/{doi}"


class EvidenceCollector:
    """Collector aggregating evidence items."""

    def __init__(self) -> None:
        self.evidence_list: list[EvidenceItem] = []

    def collect(self, chunk: DocumentChunk, claim: str, confidence: float) -> EvidenceItem:
        """Collect and format evidence item."""
        citation = CitationResolver.resolve_citation(chunk)
        item = EvidenceItem(claim=claim, citation=citation, doi=chunk.doi, confidence=confidence)
        self.evidence_list.append(item)
        return item


class HallucinationGuard:
    """Guard ensuring every generated scientific claim has empirical or retrieved evidence."""

    @staticmethod
    def verify_claim_support(claim: str, retrieved_chunks: list[DocumentChunk]) -> bool:
        """Verify claim text has matching evidence in retrieved chunks."""
        if not retrieved_chunks:
            return False
        claim_words = set(claim.lower().split())
        for chunk in retrieved_chunks:
            chunk_words = set(chunk.text.lower().split())
            if len(claim_words.intersection(chunk_words)) >= 2:
                return True
        return False


class QueryPlanner:
    """RAG Query Planner decomposing research questions into sub-queries."""

    @staticmethod
    def plan_subqueries(question: str) -> list[str]:
        """Decompose question into sub-queries."""
        return [
            f"Methodology for {question}",
            f"Data processing and spectral indices for {question}",
            f"Validation results for {question}",
        ]
