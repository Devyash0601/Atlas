"""ArtifactStore storing immutable, versioned workflow artifacts with lineage."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class WorkflowArtifact:
    """Immutable workflow artifact container."""

    artifact_uuid: str
    artifact_type: str
    producer_node_id: str
    content: dict[str, Any]
    confidence: float = 1.0
    consumer_node_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)
    version: int = 1
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class ArtifactStore:
    """Immutable versioned storage for workflow artifacts."""

    def __init__(self) -> None:
        self._artifacts: dict[str, WorkflowArtifact] = {}
        self._by_type: dict[str, list[WorkflowArtifact]] = {}

    def store_artifact(
        self,
        artifact_type: str,
        producer_node_id: str,
        content: dict[str, Any],
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
        references: list[str] | None = None,
    ) -> WorkflowArtifact:
        """Store new immutable artifact with auto-generated UUID and version tracking."""
        artifact_id = str(uuid.uuid4())
        existing_version = len(self._by_type.get(artifact_type, [])) + 1

        artifact = WorkflowArtifact(
            artifact_uuid=artifact_id,
            artifact_type=artifact_type,
            producer_node_id=producer_node_id,
            content=content,
            confidence=confidence,
            metadata=metadata or {},
            references=references or [],
            version=existing_version,
        )

        self._artifacts[artifact_id] = artifact

        if artifact_type not in self._by_type:
            self._by_type[artifact_type] = []
        self._by_type[artifact_type].append(artifact)

        return artifact

    def get_artifact(self, artifact_uuid: str) -> WorkflowArtifact | None:
        """Retrieve artifact by UUID."""
        return self._artifacts.get(artifact_uuid)

    def get_latest_by_type(self, artifact_type: str) -> WorkflowArtifact | None:
        """Get latest version of artifact by type."""
        items = self._by_type.get(artifact_type, [])
        return items[-1] if items else None

    def list_artifacts(self) -> list[WorkflowArtifact]:
        """Return list of all stored artifacts."""
        return list(self._artifacts.values())
