"""ArtifactCollector gathering and indexing artifacts from WorkflowArtifactBundle."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkflowArtifactBundle:
    """Bundle containing all immutable workflow outputs required for report generation."""

    research_question: str
    evidence_items: list[dict[str, Any]] = field(default_factory=list)
    verified_claims: list[dict[str, Any]] = field(default_factory=list)
    ee_results: dict[str, Any] = field(default_factory=dict)
    figures: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class ArtifactCollector:
    """Collector validating and indexing workflow artifact bundle entries."""

    def __init__(self, bundle: WorkflowArtifactBundle) -> None:
        self.bundle = bundle

    def get_evidence_list(self) -> list[dict[str, Any]]:
        """Return list of retrieved scientific evidence items."""
        return self.bundle.evidence_items

    def get_verified_claims(self) -> list[dict[str, Any]]:
        """Return list of verified research claims."""
        return self.bundle.verified_claims

    def get_ee_summary(self) -> dict[str, Any]:
        """Return Earth Engine computation summary dictionary."""
        return self.bundle.ee_results

    def get_execution_history(self) -> list[dict[str, Any]]:
        """Return workflow execution history logs."""
        return self.bundle.execution_history
