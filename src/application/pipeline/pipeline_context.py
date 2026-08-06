"""PipelineContext holding research UUID, question, parameters, state, and metrics."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class PipelineContext:
    """Context object carrying state across pipeline execution stages."""

    research_uuid: str
    question: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    dataset_preference: str | None = None
    output_format: str = "all"
    prompt_version: str = "1.0.0"
    model_version: str = "qwen2.5-coder:7b"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    research_plan: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
