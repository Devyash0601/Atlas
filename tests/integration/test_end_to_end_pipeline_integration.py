"""Integration tests for Phase A & Sprint 2-5 End-to-End Research Pipeline."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx

from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.pipeline_events import PipelineCompleted, PipelineStarted
from src.application.pipeline.pipeline_executor import PipelineExecutor
from src.application.pipeline.pipeline_metrics import PipelineMetrics
from src.application.pipeline.pipeline_state import PipelineState
from src.application.pipeline.pipeline_validator import PipelineValidator
from src.application.pipeline.research_pipeline import ResearchPipeline
from src.interfaces.cli.research_command import main as cli_main

_orig_client = httpx.AsyncClient


def _mock_ollama_client(**kw):
    """Mock transport for Ollama HTTP API responses."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        prompt_text = request.content.decode("utf-8") if request.content else ""
        if "Amazon" in prompt_text or "deforestation" in prompt_text:
            obj = "Analyze deforestation and soil moisture in Amazon"
            indices = ["NDWI", "SMM"]
            study_area = "Amazon Basin"
        else:
            obj = "Evaluate land surface temperature trends in Hyderabad"
            indices = ["NDVI", "LST"]
            study_area = "Hyderabad, India"

        return httpx.Response(
            200,
            json={
                "model": "qwen2.5-coder:7b",
                "response": json.dumps(
                    {
                        "objective": obj,
                        "study_area": study_area,
                        "time_range": {"start": "2016-01-01", "end": "2025-12-31"},
                        "datasets": ["COPERNICUS/S2_SR_HARMONIZED"],
                        "indices": indices,
                        "gee_operations": ["LoadCollection", "NDVI"],
                        "deliverables": ["Report", "Map"],
                    }
                ),
                "done": True,
                "prompt_eval_count": 20,
                "eval_count": 30,
                "total_duration": 100000000,
            },
        )

    kw["transport"] = httpx.MockTransport(mock_handler)
    return _orig_client(**kw)


def test_pipeline_context_and_state() -> None:
    """Verify PipelineContext and PipelineState stage tracking across all 11 stages."""
    context = PipelineContext(
        research_uuid="res_int_01",
        question="How has land surface temperature changed in Hyderabad between 2016 and 2025?",
        location="Hyderabad, India",
    )
    assert context.research_uuid == "res_int_01"
    assert context.research_plan is None

    state = PipelineState()
    assert len(state.STAGES) == 11
    state.mark_stage_completed("STAGE_1_QUESTION_VALIDATION")
    assert "STAGE_1_QUESTION_VALIDATION" in state.completed_stages


def test_pipeline_executor_end_to_end(tmp_path: Path) -> None:
    """Verify PipelineExecutor 11-stage research pipeline execution."""
    executor = PipelineExecutor()
    context = PipelineContext(
        research_uuid="res_int_02",
        question="Evaluating Assam flood extents in 2022 using Sentinel-2.",
        location="Assam, India",
        start_date="2022-05-01",
        end_date="2022-09-30",
    )
    state = PipelineState()
    metrics = PipelineMetrics()

    with patch.object(httpx, "AsyncClient", _mock_ollama_client):
        result = executor.execute_pipeline(
            context=context,
            state=state,
            metrics=metrics,
            output_base_dir=tmp_path,
        )

    assert result["status"] == "COMPLETED"
    assert context.research_plan is not None
    assert len(context.metadata.get("evidence_items", [])) > 0
    assert len(context.metadata.get("verified_claims", [])) > 0
    project_dir = Path(result["project_dir"])
    assert project_dir.exists()
    assert PipelineValidator.validate_project_directory(project_dir) is True

    report_md = (project_dir / "report.md").read_text(encoding="utf-8")
    assert "ATLAS Team" not in report_md
    assert "Satellite Remote Sensing Methodologies" not in report_md


def test_dynamic_rag_literature_retrieval_and_claims(tmp_path: Path) -> None:
    """Verify Stage 3 & 4 dynamic retrieval yields distinct results."""
    executor = PipelineExecutor()

    ctx_a = PipelineContext(
        research_uuid="res_dyn_a",
        question="How has urban expansion affected land surface temperature in Hyderabad?",
        location="Hyderabad",
    )
    ctx_b = PipelineContext(
        research_uuid="res_dyn_b",
        question="How has deforestation affected soil moisture in the Amazon Basin?",
        location="Amazon Basin",
    )

    with patch.object(httpx, "AsyncClient", _mock_ollama_client):
        executor.execute_pipeline(ctx_a, PipelineState(), PipelineMetrics(), tmp_path / "run_a")
        executor.execute_pipeline(ctx_b, PipelineState(), PipelineMetrics(), tmp_path / "run_b")

    papers_a = [p["citation_id"] for p in ctx_a.metadata.get("evidence_items", [])]
    papers_b = [p["citation_id"] for p in ctx_b.metadata.get("evidence_items", [])]

    claims_a = [c["claim"] for c in ctx_a.metadata.get("verified_claims", [])]
    claims_b = [c["claim"] for c in ctx_b.metadata.get("verified_claims", [])]

    assert len(papers_a) > 0
    assert len(papers_b) > 0
    assert set(papers_a) != set(papers_b)
    assert set(claims_a) != set(claims_b)


def test_dynamic_gee_plan_generation(tmp_path: Path) -> None:
    """Verify Stage 6 generates distinct GEE plans for distinct research questions."""
    executor = PipelineExecutor()

    ctx_a = PipelineContext(
        research_uuid="res_gee_a",
        question="How has urban expansion affected land surface temperature in Hyderabad?",
        location="Hyderabad",
    )
    ctx_b = PipelineContext(
        research_uuid="res_gee_b",
        question="How has deforestation affected soil moisture in the Amazon Basin?",
        location="Amazon Basin",
    )

    with patch.object(httpx, "AsyncClient", _mock_ollama_client):
        executor.execute_pipeline(ctx_a, PipelineState(), PipelineMetrics(), tmp_path / "run_a")
        executor.execute_pipeline(ctx_b, PipelineState(), PipelineMetrics(), tmp_path / "run_b")

    plan_a = ctx_a.metadata.get("gee_plan")
    plan_b = ctx_b.metadata.get("gee_plan")

    assert plan_a is not None
    assert plan_b is not None
    assert plan_a.spatial_bounds != plan_b.spatial_bounds
    assert [op.op_type for op in plan_a.operations] != [op.op_type for op in plan_b.operations]


def test_research_pipeline_facade_and_cli(tmp_path: Path) -> None:
    """Verify ResearchPipeline facade and CLI command invocation."""
    pipeline = ResearchPipeline()

    with patch.object(httpx, "AsyncClient", _mock_ollama_client):
        result = pipeline.run_research(
            question="Western Ghats forest change between 2015 and 2025.",
            output_dir=tmp_path,
        )
        assert result["status"] == "COMPLETED"

        # Test CLI invocation
        cli_args = [
            "--question",
            "Assam flood evolution 2022",
            "--location",
            "Assam",
            "--output",
            str(tmp_path),
        ]
        exit_code = cli_main(cli_args)
        assert exit_code == 0


def test_pipeline_events_instantiation() -> None:
    """Verify pipeline domain events inheritance."""
    e1 = PipelineStarted(research_uuid="res_ev_1", question="Q1")
    e2 = PipelineCompleted(research_uuid="res_ev_1", project_dir="projects/p1")
    assert e1.research_uuid == "res_ev_1"
    assert e2.project_dir == "projects/p1"
