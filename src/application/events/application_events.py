"""Application-level orchestration events."""

import uuid
from datetime import UTC, datetime


class ApplicationEvent:
    """Base application event representing orchestration state changes."""

    def __init__(
        self,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        self._event_id = event_id or uuid.uuid4()
        self._occurred_at = occurred_at or datetime.now(UTC)

    @property
    def event_id(self) -> uuid.UUID:
        """Return event UUID."""
        return self._event_id

    @property
    def occurred_at(self) -> datetime:
        """Return occurrence UTC timestamp."""
        return self._occurred_at


class ProjectStarted(ApplicationEvent):
    """Event emitted when a project starts processing."""

    def __init__(self, project_id: str) -> None:
        super().__init__()
        self.project_id = project_id


class WorkflowApproved(ApplicationEvent):
    """Event emitted when a workflow is approved by a researcher."""

    def __init__(self, workflow_id: str, approver_user_id: str) -> None:
        super().__init__()
        self.workflow_id = workflow_id
        self.approver_user_id = approver_user_id


class WorkflowCompleted(ApplicationEvent):
    """Event emitted when workflow execution completes successfully."""

    def __init__(self, workflow_id: str) -> None:
        super().__init__()
        self.workflow_id = workflow_id


class ReportRequested(ApplicationEvent):
    """Event emitted when a report generation task is requested."""

    def __init__(self, workflow_id: str) -> None:
        super().__init__()
        self.workflow_id = workflow_id


class EvidenceVerified(ApplicationEvent):
    """Event emitted when evidence claim verification finishes."""

    def __init__(self, verification_id: str, workflow_id: str, status: str) -> None:
        super().__init__()
        self.verification_id = verification_id
        self.workflow_id = workflow_id
        self.status = status
