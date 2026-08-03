"""Report domain events."""

import uuid
from datetime import datetime

from src.domain.base.domain_event import DomainEvent


class ReportGenerated(DomainEvent):
    """Event emitted when a scientific report artifact is generated."""

    def __init__(
        self,
        report_id: uuid.UUID,
        workflow_id: uuid.UUID,
        markdown_path: str,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.report_id = report_id
        self.workflow_id = workflow_id
        self.markdown_path = markdown_path
