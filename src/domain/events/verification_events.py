"""Evidence and verification domain events."""

import uuid
from datetime import datetime

from src.domain.base.domain_event import DomainEvent
from src.domain.enums.verification_status import VerificationStatus


class EvidenceAdded(DomainEvent):
    """Event emitted when evidence is attached to a workflow."""

    def __init__(
        self,
        evidence_id: uuid.UUID,
        workflow_id: uuid.UUID,
        source_citation: str,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.evidence_id = evidence_id
        self.workflow_id = workflow_id
        self.source_citation = source_citation


class VerificationCompleted(DomainEvent):
    """Event emitted when scientific verification completes."""

    def __init__(
        self,
        verification_id: uuid.UUID,
        workflow_id: uuid.UUID,
        status: VerificationStatus,
        confidence_score: float,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.verification_id = verification_id
        self.workflow_id = workflow_id
        self.status = status
        self.confidence_score = confidence_score
