"""Workflow domain entity."""

import uuid
from datetime import datetime
from typing import Any

from src.domain.base.entity import Entity
from src.domain.enums.workflow_status import WorkflowStatus
from src.domain.exceptions.domain_exceptions import BusinessRuleViolationError, StateTransitionError


class Workflow(Entity):
    """Workflow entity maintaining execution plan schemas and human approval status."""

    def __init__(
        self,
        project_id: uuid.UUID,
        planner_output: dict[str, Any],
        status: WorkflowStatus = WorkflowStatus.DRAFT,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Workflow entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._project_id = project_id
        self._planner_output = planner_output
        self._status = status

    @property
    def project_id(self) -> uuid.UUID:
        """Return parent project UUID."""
        return self._project_id

    @property
    def planner_output(self) -> dict[str, Any]:
        """Return structured planner output plan."""
        return dict(self._planner_output)

    @property
    def status(self) -> WorkflowStatus:
        """Return current workflow status."""
        return self._status

    def approve(self) -> None:
        """Approve workflow for execution."""
        if self._status not in (WorkflowStatus.DRAFT, WorkflowStatus.PENDING_APPROVAL):
            msg = f"Cannot approve workflow currently in state '{self._status}'"
            raise StateTransitionError(msg)
        self._status = WorkflowStatus.APPROVED
        self.touch()

    def execute(self) -> None:
        """Start workflow execution (Business Rule: Workflow MUST be APPROVED before execution)."""
        if self._status != WorkflowStatus.APPROVED:
            raise BusinessRuleViolationError(
                f"Workflow cannot execute before approval. Current status is '{self._status}'"
            )
        self._status = WorkflowStatus.EXECUTING
        self.touch()

    def mark_completed(self) -> None:
        """Mark workflow as successfully completed."""
        if self._status != WorkflowStatus.EXECUTING:
            raise StateTransitionError(f"Cannot complete workflow in state '{self._status}'")
        self._status = WorkflowStatus.COMPLETED
        self.touch()

    def mark_failed(self) -> None:
        """Mark workflow execution as failed."""
        self._status = WorkflowStatus.FAILED
        self.touch()
