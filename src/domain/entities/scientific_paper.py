"""ScientificPaper domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity


class ScientificPaper(Entity):
    """ScientificPaper entity representing literature references."""

    def __init__(
        self,
        title: str,
        authors: list[str],
        year: int,
        doi: str,
        abstract: str,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize ScientificPaper entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._title = title.strip()
        self._authors = list(authors)
        self._year = year
        self._doi = doi.strip()
        self._abstract = abstract.strip()

    @property
    def title(self) -> str:
        """Return paper title."""
        return self._title

    @property
    def authors(self) -> list[str]:
        """Return authors list."""
        return list(self._authors)

    @property
    def year(self) -> int:
        """Return publication year."""
        return self._year

    @property
    def doi(self) -> str:
        """Return DOI identifier."""
        return self._doi

    @property
    def abstract(self) -> str:
        """Return paper abstract."""
        return self._abstract
