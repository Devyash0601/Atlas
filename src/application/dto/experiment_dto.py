"""Experiment DTO."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExperimentDTO:
    """Read-only DTO for Experiment."""

    id: str
    workflow_id: str
    parameters: dict[str, Any]
    status: str
    execution_time_seconds: float
    logs: str
    created_at: str
