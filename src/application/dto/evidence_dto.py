"""Evidence and Verification DTOs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceDTO:
    """Read-only DTO for Evidence."""

    id: str
    workflow_id: str
    source_citation: str
    claim_summary: str
    confidence_score: float
    created_at: str


@dataclass(frozen=True)
class VerificationDTO:
    """Read-only DTO for Verification."""

    id: str
    workflow_id: str
    evidence_id: str
    status: str
    confidence_score: float
    notes: str
    created_at: str
