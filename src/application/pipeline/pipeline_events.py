"""Typed pipeline domain events dispatched during 11-stage pipeline execution."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class PipelineEvent:
    """Base pipeline event."""

    research_uuid: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class PipelineStarted(PipelineEvent):
    """Dispatched when pipeline execution begins."""

    question: str = ""


@dataclass(frozen=True)
class PlanningCompleted(PipelineEvent):
    """Dispatched when research planning stage finishes."""

    pass


@dataclass(frozen=True)
class RetrievalCompleted(PipelineEvent):
    """Dispatched when scientific literature retrieval finishes."""

    citation_count: int = 0


@dataclass(frozen=True)
class VerificationCompleted(PipelineEvent):
    """Dispatched when evidence verification finishes."""

    verified_claims_count: int = 0


@dataclass(frozen=True)
class WorkflowCompleted(PipelineEvent):
    """Dispatched when workflow graph construction finishes."""

    node_count: int = 0


@dataclass(frozen=True)
class EarthEngineCompleted(PipelineEvent):
    """Dispatched when Earth Engine computation completes."""

    pixels_processed: int = 0


@dataclass(frozen=True)
class PublicationCompleted(PipelineEvent):
    """Dispatched when scientific publication report generation completes."""

    exported_files_count: int = 0


@dataclass(frozen=True)
class EvaluationCompleted(PipelineEvent):
    """Dispatched when evaluation metrics calculation finishes."""

    pass


@dataclass(frozen=True)
class PipelineCompleted(PipelineEvent):
    """Dispatched when entire 11-stage pipeline finishes successfully."""

    project_dir: str = ""


@dataclass(frozen=True)
class PipelineFailed(PipelineEvent):
    """Dispatched when pipeline execution fails."""

    failed_stage: str = ""
    error_message: str = ""
