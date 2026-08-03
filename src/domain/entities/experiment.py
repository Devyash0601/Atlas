"""Experiment domain entity."""

import uuid
from datetime import datetime
from typing import Any

from src.domain.base.entity import Entity
from src.domain.enums.artifact_type import ExecutionStatus


class Experiment(Entity):
    """Experiment entity recording computational parameters and logs."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        parameters: dict[str, Any],
        status: ExecutionStatus = ExecutionStatus.PENDING,
        execution_time_seconds: float = 0.0,
        logs: str = "",
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Experiment entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._parameters = parameters
        self._status = status
        self._execution_time_seconds = execution_time_seconds
        self._logs = logs

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def parameters(self) -> dict[str, Any]:
        """Return experiment parameters."""
        return dict(self._parameters)

    @property
    def status(self) -> ExecutionStatus:
        """Return execution status."""
        return self._status

    @property
    def execution_time_seconds(self) -> float:
        """Return execution runtime in seconds."""
        return self._execution_time_seconds

    @property
    def logs(self) -> str:
        """Return experiment execution logs."""
        return self._logs
