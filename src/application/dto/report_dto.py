"""Report DTO."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportDTO:
    """Read-only DTO for Report."""

    id: str
    workflow_id: str
    markdown_content: str
    export_path: str
    created_at: str
