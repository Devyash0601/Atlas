"""ReportContext holding research question, author, versions, git commit, and hashes."""

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _get_current_git_sha() -> str:
    """Safely fetch current git commit SHA, falling back to v1.0.0 commit hash."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        if sha:
            return sha
    except Exception:
        pass
    return "9bb27f435a61a7cfe33ee9b1c46e98cfa633747f"


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
    git_commit_hash: str = field(default_factory=_get_current_git_sha)
    config_hash: str = "sha256-default-config"
    generation_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
