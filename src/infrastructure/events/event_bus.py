"""In-memory EventBus and EventDispatchers."""

from collections.abc import Callable
from typing import Any

from src.application.events.application_events import ApplicationEvent
from src.domain.base.domain_event import DomainEvent


class EventBus:
    """Async-ready in-memory event bus routing events to subscribers."""

    def __init__(self) -> None:
        self._subscribers: dict[type, list[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: type, handler: Callable[[Any], None]) -> None:
        """Subscribe handler function to event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        """Publish event to all registered subscribers."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            handler(event)


class DomainEventDispatcher:
    """Dispatcher for domain layer events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch domain event."""
        self.event_bus.publish(event)


class ApplicationEventDispatcher:
    """Dispatcher for application layer orchestration events."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def dispatch(self, event: ApplicationEvent) -> None:
        """Dispatch application event."""
        self.event_bus.publish(event)
