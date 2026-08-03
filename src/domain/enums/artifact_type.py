"""Artifact and execution status domain enums."""

from enum import StrEnum


class ArtifactType(StrEnum):
    """Types of generated scientific artifacts."""

    GEOTIFF = "geotiff"
    PNG_PREVIEW = "png_preview"
    CSV_STATISTICS = "csv_statistics"
    JSON_METADATA = "json_metadata"
    MARKDOWN_REPORT = "markdown_report"


class ExecutionStatus(StrEnum):
    """Task execution progress status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
