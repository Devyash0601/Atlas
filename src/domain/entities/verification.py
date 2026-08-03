"""Verification domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity
from src.domain.enums.verification_status import VerificationStatus
from src.domain.value_objects.confidence_score import ConfidenceScore


class Verification(Entity):
    """Verification entity validating scientific conclusions against evidence."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        evidence_id: uuid.UUID,
        status: VerificationStatus,
        confidence: ConfidenceScore,
        notes: str = "",
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Verification entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._evidence_id = evidence_id
        self._status = status
        self._confidence = confidence
        self._notes = notes.strip()

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def evidence_id(self) -> uuid.UUID:
        """Return evidence UUID."""
        return self._evidence_id

    @property
    def status(self) -> VerificationStatus:
        """Return verification status."""
        return self._status

    @property
    def confidence(self) -> ConfidenceScore:
        """Return verification confidence score."""
        return self._confidence

    @property
    def notes(self) -> str:
        """Return verification notes."""
        return self._notes
