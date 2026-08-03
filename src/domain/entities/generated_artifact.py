"""GeneratedArtifact domain entity."""

import uuid
from datetime import datetime

from src.domain.base.entity import Entity
from src.domain.enums.artifact_type import ArtifactType


class GeneratedArtifact(Entity):
    """GeneratedArtifact entity representing files and visual outputs."""

    def __init__(
        self,
        workflow_id: uuid.UUID,
        artifact_type: ArtifactType,
        file_path: str,
        size_bytes: int,
        entity_id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize GeneratedArtifact entity."""
        super().__init__(entity_id=entity_id, created_at=created_at, updated_at=updated_at)
        self._workflow_id = workflow_id
        self._artifact_type = artifact_type
        self._file_path = file_path
        self._size_bytes = size_bytes

    @property
    def workflow_id(self) -> uuid.UUID:
        """Return workflow UUID."""
        return self._workflow_id

    @property
    def artifact_type(self) -> ArtifactType:
        """Return artifact category."""
        return self._artifact_type

    @property
    def file_path(self) -> str:
        """Return relative artifact file path."""
        return self._file_path

    @property
    def size_bytes(self) -> int:
        """Return artifact size in bytes."""
        return self._size_bytes
