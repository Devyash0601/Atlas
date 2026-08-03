"""ScientificPaper DTO."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScientificPaperDTO:
    """Read-only DTO for ScientificPaper."""

    id: str
    title: str
    authors: list[str]
    year: int
    doi: str
    abstract: str
    created_at: str
