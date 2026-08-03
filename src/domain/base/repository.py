"""Generic Repository interface contract."""

import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

from src.domain.base.entity import Entity

T = TypeVar("T", bound=Entity)


class Repository[T: Entity](ABC):
    """Abstract generic repository contract defining persistence operations for an Entity."""

    @abstractmethod
    async def save(self, entity: T) -> None:
        """Save a new entity to persistence."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> None:
        """Update an existing entity in persistence."""
        pass

    @abstractmethod
    async def delete(self, entity_id: uuid.UUID) -> None:
        """Delete an entity by its UUID identifier."""
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Retrieve an entity by UUID identifier or return None if not found."""
        pass

    @abstractmethod
    async def find_many(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Retrieve a paginated list of entities."""
        pass

    @abstractmethod
    async def exists(self, entity_id: uuid.UUID) -> bool:
        """Check if an entity exists by UUID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Return total count of entities."""
        pass
