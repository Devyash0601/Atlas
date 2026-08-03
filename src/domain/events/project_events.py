"""Project and workflow lifecycle domain events."""

import uuid
from datetime import datetime

from src.domain.base.domain_event import DomainEvent
from src.domain.enums.workflow_status import WorkflowStatus


class ProjectCreated(DomainEvent):
    """Event emitted when a new research project is created."""

    def __init__(
        self,
        project_id: uuid.UUID,
        title: str,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.project_id = project_id
        self.title = title


class WorkflowCreated(DomainEvent):
    """Event emitted when a workflow is planned for a project."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        project_id: uuid.UUID,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.workflow_id = workflow_id
        self.project_id = project_id


class WorkflowExecuted(DomainEvent):
    """Event emitted when a workflow execution completes."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        status: WorkflowStatus,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_at=occurred_at)
        self.workflow_id = workflow_id
        self.status = status
