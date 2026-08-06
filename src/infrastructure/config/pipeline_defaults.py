"""PipelineDefaults configuration constants."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PipelineDefaults:
    """Default configuration constants for end-to-end research executions."""

    model_name: str = "qwen2.5-coder:14b-instruct-q4_K_M"
    prompt_package_version: str = "1.0.0"
    default_bounding_box: list[float] = field(default_factory=lambda: [2.2, 48.5, 2.5, 49.0])
    default_start_date: str = "2024-01-01"
    default_end_date: str = "2024-12-31"
    output_directory_name: str = "projects"
    timeout_seconds: int = 600
