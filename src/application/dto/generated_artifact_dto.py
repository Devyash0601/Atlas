"""GeneratedArtifact DTO."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedArtifactDTO:
    """Read-only DTO for GeneratedArtifact."""

    id: str
    workflow_id: str
    artifact_type: str
    file_path: str
    size_bytes: int
    created_at: str
