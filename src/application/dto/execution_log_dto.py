"""ExecutionLog DTO."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionLogDTO:
    """Read-only DTO for ExecutionLog."""

    id: str
    workflow_id: str
    step_name: str
    message: str
    is_error: bool
    created_at: str
