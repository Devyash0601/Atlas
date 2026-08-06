"""ReportContext holding research question, author, versions, git commit, and hashes."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class ReportContext:
    """Immutable context metadata container for scientific reports."""

    research_uuid: str
    research_question: str
    title: str = "Automated Scientific Earth Observation Report"
    author: str = "ATLAS-EO Autonomous Scientific Platform"
    report_version: str = "1.0.0"
    workflow_version: str = "1.0.0"
    prompt_version: str = "1.0.0"
    model_version: str = "qwen2.5-coder:14b-instruct-q4_K_M"
    git_commit_hash: str = "v0.5.0-core-platform"
    config_hash: str = "sha256-default-config"
    generation_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
