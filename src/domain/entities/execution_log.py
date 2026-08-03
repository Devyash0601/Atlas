"""ExecutionLog domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity


class ExecutionLog(Entity):
    """ExecutionLog entity for auditing workflow run events."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        step_name: str,
        message: str,
        is_error: bool = False,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize ExecutionLog entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._step_name = step_name
        self._message = message
        self._is_error = is_error

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def step_name(self) -> str:
        """Return step name."""
        return self._step_name

    @property
    def message(self) -> str:
        """Return log message."""
        return self._message

    @property
    def is_error(self) -> bool:
        """Return whether log represents an error."""
        return self._is_error
