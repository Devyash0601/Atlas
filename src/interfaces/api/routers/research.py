"""FastAPI router exposing research execution, project query, and publication report endpoints."""

from fastapi import APIRouter

from src.interfaces.api.schemas.research import (
    ProjectSummary,
    ReportResponse,
    ResearchRequest,
    ResearchResponse,
)
from src.interfaces.api.services.research_service import ResearchService

router = APIRouter(tags=["Research"])


@router.post(
    "/research",
    response_model=ResearchResponse,
    summary="Execute Autonomous Research Pipeline",
    description="Trigger 11-stage autonomous Earth Observation research pipeline for question.",
)
def run_research(payload: ResearchRequest) -> ResearchResponse:
    """Execute research pipeline and return project outcome."""
    service = ResearchService()
    return service.run_research(payload)


@router.get(
    "/research/{project_id}",
    response_model=ResearchResponse,
    summary="Retrieve Executed Research Project",
    description="Fetch executed research project specification, metrics, and project directory.",
)
def get_research_project(project_id: str) -> ResearchResponse:
    """Retrieve research project by ID."""
    service = ResearchService()
    return service.get_project(project_id)


@router.get(
    "/projects",
    response_model=list[ProjectSummary],
    summary="List Executed Projects",
    description="Retrieve list of all executed research project summaries.",
)
def list_projects() -> list[ProjectSummary]:
    """List all executed research project summaries."""
    service = ResearchService()
    return service.list_projects()


@router.get(
    "/reports/{project_id}",
    response_model=ReportResponse,
    summary="Retrieve Generated Publication Report",
    description="Retrieve publication report markdown content and metadata for project ID.",
)
def get_publication_report(project_id: str) -> ReportResponse:
    """Retrieve generated publication report."""
    service = ResearchService()
    return service.get_report(project_id)
