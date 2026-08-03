"""Evidence domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity
from src.domain.exceptions.domain_exceptions import BusinessRuleViolationError
from src.domain.value_objects.confidence_score import ConfidenceScore


class Evidence(Entity):
    """Evidence entity linking scientific claims to sources."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        source_citation: str,
        claim_summary: str,
        confidence: ConfidenceScore,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Evidence entity (requires non-empty source citation)."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        if not source_citation or not source_citation.strip():
            msg = "Evidence cannot exist without a valid source citation"
            raise BusinessRuleViolationError(msg)
        if not claim_summary or not claim_summary.strip():
            raise BusinessRuleViolationError("Evidence claim summary cannot be empty")

        self._workflow_id = workflow_id
        self._source_citation = source_citation.strip()
        self._claim_summary = claim_summary.strip()
        self._confidence = confidence

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return parent workflow UUID."""
        return self._workflow_id

    @property
    def source_citation(self) -> str:
        """Return source citation text."""
        return self._source_citation

    @property
    def claim_summary(self) -> str:
        """Return claim summary."""
        return self._claim_summary

    @property
    def confidence(self) -> ConfidenceScore:
        """Return confidence score."""
        return self._confidence
