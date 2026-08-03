"""Project and workflow execution commands."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CreateProjectCommand:
    """Command to initialize a new research project."""

    title: str
    question_text: str
    region_name: str
    south_west_lat: float
    south_west_lon: float
    north_east_lat: float
    north_east_lon: float
    user_id: str


@dataclass(frozen=True)
class CreateWorkflowCommand:
    """Command to plan a new execution workflow."""

    project_id: str
    planner_output: dict[str, Any]


@dataclass(frozen=True)
class ApproveWorkflowCommand:
    """Command to approve a workflow for execution."""

    workflow_id: str
    approver_user_id: str


@dataclass(frozen=True)
class ExecuteWorkflowCommand:
    """Command to trigger workflow execution."""

    workflow_id: str
