"""Report domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity


class Report(Entity):
    """Report entity representing generated publication markdown reports."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        markdown_content: str,
        export_path: str,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Report entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._markdown_content = markdown_content
        self._export_path = export_path

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def markdown_content(self) -> str:
        """Return raw markdown report content."""
        return self._markdown_content

    @property
    def export_path(self) -> str:
        """Return saved report export file path."""
        return self._export_path
