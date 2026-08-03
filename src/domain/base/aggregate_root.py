"""Base Aggregate Root class managing domain events."""

import uuid
from datetime import datetime

from src.domain.base.domain_event import DomainEvent
from src.domain.base.entity import Entity


class AggregateRoot(Entity):
    """Abstract aggregate root entity responsible for consistency boundaries and domain events."""

    def __init__(
        self,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize aggregate root and event collection."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._domain_events: list[DomainEvent] = []

    def add_event(self, event: DomainEvent) -> None:
        """Record a new domain event."""
        self._domain_events.append(event)

    def clear_events(self) -> None:
        """Clear all pending domain events."""
        self._domain_events.clear()

    def pull_events(self) -> list[DomainEvent]:
        """Retrieve and clear all accumulated domain events."""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Return a copy of pending domain events."""
        return list(self._domain_events)
