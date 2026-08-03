"""Project status domain enum."""

from enum import StrEnum


class ProjectStatus(StrEnum):
    """Lifecycle status states for a research project."""

    CREATED = "created"
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
