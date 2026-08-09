"""Domain service layer for orchestrating research pipeline executions and project queries."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from src.application.pipeline.research_pipeline import ResearchPipeline
from src.interfaces.api.schemas.research import (
    ProjectSummary,
    ReportResponse,
    ResearchRequest,
    ResearchResponse,
)
from src.shared.exceptions.base import AtlasException, NotFoundException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class ResearchService:
    """Domain service managing research execution, response translation, and project storage.

    NOTE: Project storage relies on a temporary in-memory store (_projects_store).
    This temporary implementation will be replaced by database persistence in a future phase.
    """

    _projects_store: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, pipeline: ResearchPipeline | None = None) -> None:
        self.pipeline = pipeline or ResearchPipeline()

    def run_research(self, request_payload: ResearchRequest) -> ResearchResponse:
        """Execute autonomous 11-stage research pipeline and store project metadata."""
        logger.info(
            "Research started",
            question=request_payload.question,
            location=request_payload.location,
        )

        try:
            pipeline_result = self.pipeline.run_research(
                question=request_payload.question,
                location=request_payload.location,
                start_date=request_payload.start_date,
                end_date=request_payload.end_date,
                dataset_preference=request_payload.dataset_preference,
            )
        except Exception as err:
            logger.error("Research failed", error=str(err), question=request_payload.question)
            raise AtlasException(f"Research pipeline execution failed: {err}") from err

        project_dir = Path(pipeline_result["project_dir"])
        project_id = project_dir.name.replace("Research_", "res_")
        if not project_id.startswith("res_"):
            project_id = f"res_{project_id}"

        # Read generated markdown report content if available
        report_path = project_dir / "report.md"
        report_content = ""
        if report_path.exists():
            report_content = report_path.read_text(encoding="utf-8")

        metadata_path = project_dir / "metadata.json"
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            import json

            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except Exception:
                metadata = {}

        created_at = datetime.now(UTC).isoformat()

        project_data: dict[str, Any] = {
            "project_id": project_id,
            "question": request_payload.question,
            "location": request_payload.location,
            "status": pipeline_result.get("status", "COMPLETED"),
            "project_dir": str(project_dir),
            "metrics": pipeline_result.get("metrics", {}),
            "report_content": report_content,
            "metadata": metadata,
            "created_at": created_at,
        }

        # Save to temporary in-memory store
        self._projects_store[project_id] = project_data

        logger.info("Research completed", project_id=project_id, status=project_data["status"])

        return ResearchResponse(
            project_id=project_id,
            question=request_payload.question,
            location=request_payload.location,
            status=project_data["status"],
            project_dir=project_data["project_dir"],
            metrics=project_data["metrics"],
            created_at=created_at,
        )

    def get_project(self, project_id: str) -> ResearchResponse:
        """Retrieve previously executed research project by ID."""
        if project_id not in self._projects_store:
            raise NotFoundException(f"Research project '{project_id}' not found.")

        proj = self._projects_store[project_id]
        return ResearchResponse(
            project_id=proj["project_id"],
            question=proj["question"],
            location=proj["location"],
            status=proj["status"],
            project_dir=proj["project_dir"],
            metrics=proj["metrics"],
            created_at=proj["created_at"],
        )

    def list_projects(self) -> list[ProjectSummary]:
        """Return list of all executed research project summaries."""
        summaries: list[ProjectSummary] = []
        for proj in self._projects_store.values():
            summaries.append(
                ProjectSummary(
                    project_id=proj["project_id"],
                    question=proj["question"],
                    location=proj["location"],
                    status=proj["status"],
                    created_at=proj["created_at"],
                )
            )
        return summaries

    def get_report(self, project_id: str) -> ReportResponse:
        """Retrieve publication report content and metadata for specified project ID."""
        if project_id not in self._projects_store:
            raise NotFoundException(f"Report for project '{project_id}' not found.")

        proj = self._projects_store[project_id]
        return ReportResponse(
            project_id=proj["project_id"],
            question=proj["question"],
            report_content=proj["report_content"],
            metadata=proj["metadata"],
        )
