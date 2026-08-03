"""Base Entity class for domain models with UUID identity."""

import uuid
from datetime import UTC, datetime


class Entity:
    """Abstract base class for all domain entities."""

    def __init__(
        self,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize domain entity with identity and UTC timestamps."""
        now = datetime.now(UTC)
        self._id: uuid.UUID = entity_id or uuid.uuid4()
        self._created_at: datetime = created_at or now
        self._updated_at: datetime = updated_at or now

    @property
    def id(self) -> uuid.UUID:
        """Return the unique entity UUID identifier."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Return UTC creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Return UTC last updated timestamp."""
        return self._updated_at

    def touch(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Entities are equal if they have the same type and UUID."""
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash entity by type and UUID."""
        return hash((self.__class__, self._id))

    def __repr__(self) -> str:
        """Represent entity string format."""
        return f"<{self.__class__.__name__} id={self._id}>"
