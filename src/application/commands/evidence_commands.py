"""Evidence and verification commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AddEvidenceCommand:
    """Command to attach gathered evidence to a workflow."""

    workflow_id: str
    source_citation: str
    claim_summary: str
    confidence_score: float


@dataclass(frozen=True)
class VerifyEvidenceCommand:
    """Command to execute claim verification against evidence."""

    workflow_id: str
    evidence_id: str
    status: str
    confidence_score: float
    notes: str = ""
