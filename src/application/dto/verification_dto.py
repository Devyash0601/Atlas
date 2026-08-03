"""Verification DTO."""

from dataclasses import dataclass


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
