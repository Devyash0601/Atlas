"""Base class for all domain events."""

import uuid
from datetime import UTC, datetime


class DomainEvent:
    """Immutable domain event representing a state change in the business domain."""

    def __init__(
        self,
        event_id: uuid.UUID | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        """Initialize domain event with unique event ID and occurred timestamp."""
        self._event_id: uuid.UUID = event_id or uuid.uuid4()
        self._occurred_at: datetime = occurred_at or datetime.now(UTC)

    @property
    def event_id(self) -> uuid.UUID:
        """Return unique event identifier."""
        return self._event_id

    @property
    def occurred_at(self) -> datetime:
        """Return UTC timestamp when event occurred."""
        return self._occurred_at

    def __repr__(self) -> str:
        """Represent domain event in string format."""
        return f"<{self.__class__.__name__} id={self._event_id} at={self._occurred_at.isoformat()}>"
