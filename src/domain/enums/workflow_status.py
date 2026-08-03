"""Workflow status domain enum."""

from enum import StrEnum


class WorkflowStatus(StrEnum):
    """Lifecycle status states for an execution workflow."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
