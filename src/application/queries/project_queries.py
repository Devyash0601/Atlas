"""Read-only query specifications."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetProjectQuery:
    """Query to fetch a single research project by UUID."""

    project_id: str


@dataclass(frozen=True)
class GetWorkflowQuery:
    """Query to fetch a workflow by UUID."""

    workflow_id: str


@dataclass(frozen=True)
class ListProjectsQuery:
    """Query to list research projects owned by a user."""

    user_id: str
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class ListDatasetsQuery:
    """Query to list datasets attached to a workflow."""

    workflow_id: str


@dataclass(frozen=True)
class ListEvidenceQuery:
    """Query to list evidence gathered for a workflow."""

    workflow_id: str


@dataclass(frozen=True)
class GetReportQuery:
    """Query to retrieve generated report for a workflow."""

    workflow_id: str


@dataclass(frozen=True)
class SearchScientificPapersQuery:
    """Query to search scientific literature papers."""

    query_text: str
    limit: int = 10
