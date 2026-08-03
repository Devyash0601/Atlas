"""Workflow Data Transfer Object (DTO)."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowDTO:
    """Read-only DTO representing a workflow execution plan."""

    id: str
    project_id: str
    planner_output: dict[str, Any]
    status: str
    created_at: str
    updated_at: str
