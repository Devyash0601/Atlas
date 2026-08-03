"""EvidenceGraph linking claims, supporting chunks, papers, figures, tables, and confidence."""

from dataclasses import dataclass, field
from typing import Any

from src.infrastructure.rag.chunking import DocumentChunk


@dataclass
class EvidenceGraphNode:
    """Node in evidence graph."""

    claim_text: str
    supporting_chunks: list[DocumentChunk] = field(default_factory=list)
    supporting_papers: list[str] = field(default_factory=list)
    supporting_figures: list[str] = field(default_factory=list)
    supporting_tables: list[str] = field(default_factory=list)
    confidence: float = 0.95
    contradictions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


class EvidenceGraph:
    """Graph connecting scientific claims to empirical evidence."""

    def __init__(self) -> None:
        self.evidence_nodes: list[EvidenceGraphNode] = []

    def add_evidence_node(self, node: EvidenceGraphNode) -> None:
        """Add node to evidence graph."""
        self.evidence_nodes.append(node)

    def calculate_overall_confidence(self) -> float:
        """Compute overall average confidence across all evidence nodes."""
        if not self.evidence_nodes:
            return 0.0
        return round(sum(n.confidence for n in self.evidence_nodes) / len(self.evidence_nodes), 3)

    def get_summary(self) -> dict[str, Any]:
        """Return summary of evidence graph payload."""
        return {
            "evidence_count": len(self.evidence_nodes),
            "overall_confidence": self.calculate_overall_confidence(),
            "papers_cited": list({p for n in self.evidence_nodes for p in n.supporting_papers}),
        }
