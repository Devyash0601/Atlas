"""Unit and API integration tests for Research REST API endpoints and ResearchService."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.interfaces.api.main import app
from src.interfaces.api.schemas.research import ResearchRequest
from src.interfaces.api.services.research_service import ResearchService

client = TestClient(app)


def test_research_service_unit(tmp_path: Path) -> None:
    """Verify ResearchService unit execution, project storing, and error handling."""
    mock_pipeline = MagicMock()
    mock_proj_dir = tmp_path / "Research_test123"
    mock_proj_dir.mkdir(parents=True, exist_ok=True)
    (mock_proj_dir / "report.md").write_text("# Test Report", encoding="utf-8")
    (mock_proj_dir / "metadata.json").write_text('{"title": "Test Metadata"}', encoding="utf-8")

    mock_pipeline.run_research.return_value = {
        "status": "COMPLETED",
        "project_dir": str(mock_proj_dir),
        "metrics": {"duration_sec": 1.5},
    }

    service = ResearchService(pipeline=mock_pipeline)
    req = ResearchRequest(
        question="How has land surface temperature changed in Hyderabad?",
        location="Hyderabad",
    )

    res = service.run_research(req)
    assert res.project_id == "res_test123"
    assert res.status == "COMPLETED"

    # Verify project retrieval
    proj = service.get_project("res_test123")
    assert proj.question == req.question

    # Verify project list
    projects = service.list_projects()
    assert len(projects) >= 1

    # Verify report retrieval
    report = service.get_report("res_test123")
    assert report.report_content == "# Test Report"
    assert report.metadata.get("title") == "Test Metadata"


def test_post_research_endpoint(tmp_path: Path) -> None:
    """Verify POST /api/v1/research endpoint executes pipeline and returns HTTP 200 JSON."""
    mock_proj_dir = tmp_path / "Research_api001"
    mock_proj_dir.mkdir(parents=True, exist_ok=True)
    (mock_proj_dir / "report.md").write_text("# API Test Report", encoding="utf-8")

    mock_result = {
        "status": "COMPLETED",
        "project_dir": str(mock_proj_dir),
        "metrics": {"total_duration_sec": 2.1},
    }

    with patch(
        "src.application.pipeline.research_pipeline.ResearchPipeline.run_research",
        return_value=mock_result,
    ):
        payload = {
            "question": "How has urban growth affected surface temperature in Hyderabad?",
            "location": "Hyderabad",
            "start_date": "2016-01-01",
            "end_date": "2025-12-31",
        }
        resp = client.post("/api/v1/research", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["project_id"] == "res_api001"
        assert data["status"] == "COMPLETED"


def test_get_projects_and_reports_endpoints(tmp_path: Path) -> None:
    """Verify GET /api/v1/projects and GET /api/v1/reports/{project_id} endpoints."""
    mock_proj_dir = tmp_path / "Research_api002"
    mock_proj_dir.mkdir(parents=True, exist_ok=True)
    (mock_proj_dir / "report.md").write_text("# Report 002 Content", encoding="utf-8")

    mock_result = {
        "status": "COMPLETED",
        "project_dir": str(mock_proj_dir),
        "metrics": {},
    }

    with patch(
        "src.application.pipeline.research_pipeline.ResearchPipeline.run_research",
        return_value=mock_result,
    ):
        client.post(
            "/api/v1/research", json={"question": "Deforestation in Amazon", "location": "Amazon"}
        )

    # Test GET /projects
    resp_list = client.get("/api/v1/projects")
    assert resp_list.status_code == 200
    projects = resp_list.json()
    assert isinstance(projects, list)
    assert any(p["project_id"] == "res_api002" for p in projects)

    # Test GET /research/{project_id}
    resp_proj = client.get("/api/v1/research/res_api002")
    assert resp_proj.status_code == 200
    assert resp_proj.json()["project_id"] == "res_api002"

    # Test GET /reports/{project_id}
    resp_rep = client.get("/api/v1/reports/res_api002")
    assert resp_rep.status_code == 200
    assert "# Report 002 Content" in resp_rep.json()["report_content"]

    # Test GET 404 for invalid project_id
    resp_404 = client.get("/api/v1/research/invalid_project_id")
    assert resp_404.status_code == 404
