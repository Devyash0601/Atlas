"""Unit tests verifying report pipeline correctness, DAG topology, and section numbering."""

import tempfile
from pathlib import Path

from src.application.pipeline.pipeline_context import PipelineContext
from src.application.pipeline.pipeline_executor import PipelineExecutor
from src.application.pipeline.pipeline_metrics import PipelineMetrics
from src.application.pipeline.pipeline_state import PipelineState
from src.application.publication.artifact_collector import WorkflowArtifactBundle
from src.application.publication.limitations_generator import LimitationsGenerator
from src.application.publication.report_builder import ReportBuilder
from src.application.publication.report_context import ReportContext
from src.application.publication.workflow_summary import WorkflowSummaryGenerator


def test_report_context_git_commit_hash() -> None:
    """Verify ReportContext uses real git commit SHA or v1.0.0 SHA instead of v0.5.0 tag."""
    ctx = ReportContext(research_uuid="res_12345", research_question="Test question?")
    assert ctx.git_commit_hash != "v0.5.0-core-platform"
    assert len(ctx.git_commit_hash) >= 7
    assert ctx.report_version == "1.0.0"
    assert ctx.workflow_version == "1.0.0"


def test_workflow_summary_dynamic_dag_rendering() -> None:
    """Verify WorkflowSummaryGenerator renders 7 DAG nodes and actual execution runtime."""
    history = [
        {
            "node_id": f"node_{i}",
            "task_type": f"Task_{i}",
            "status": "COMPLETED",
            "duration_sec": 0.1 * i,
        }
        for i in range(1, 8)
    ]
    metrics = {"total_execution_time_sec": 12.93}

    summary_text = WorkflowSummaryGenerator.generate_workflow_summary(history, metrics)

    assert "7 nodes" in summary_text
    assert "7-stage Directed Acyclic Graph" in summary_text
    assert "- **Total Execution Time**: 12.93 seconds" in summary_text
    assert "1. **node_1** (`Task_1`): COMPLETED (0.100s)" in summary_text
    assert "7. **node_7** (`Task_7`): COMPLETED (0.700s)" in summary_text


def test_limitations_generator_section_5_numbering() -> None:
    """Verify LimitationsGenerator uses H1 '# 5. Discussion & Limitations' structure."""
    text = LimitationsGenerator.generate_limitations([], [])
    assert "# 5. Discussion & Limitations" in text
    assert "## 5.1 Threats to Validity & System Constraints" in text
    assert "## 5.2 Future Work" in text
    assert "## Discussion & Limitations" not in text


def test_report_builder_results_and_analysis_section_rendering() -> None:
    """Verify ReportBuilder renders spatial analysis statistics in Section 4."""
    rq = "Does NDBI correlate with LST?"
    context = ReportContext(research_uuid="res_test", research_question=rq)
    bundle = WorkflowArtifactBundle(
        research_question=rq,
        ee_results={
            "pixels_processed": 500000,
            "relationship_analysis": {
                "ndbi": {"mean_change": 0.0043},
                "lst": {"mean_change": -2.937},
                "correlation": {"pearson_r": 0.1926, "spearman_rho": 0.0998},
                "regression": {"slope": 5.2374, "intercept": -2.9598, "r_squared": 0.0371},
                "sample_size": 5000,
            },
        },
        execution_history=[
            {
                "node_id": f"node_{i}",
                "task_type": f"Task_{i}",
                "status": "COMPLETED",
                "duration_sec": 0.1,
            }
            for i in range(1, 8)
        ],
        metrics={"total_execution_time_sec": 8.5},
    )

    builder = ReportBuilder(context=context)
    report = builder.build(bundle)

    # 1. Section 4 Results & Analysis verification
    assert "# 4. Results & Analysis" in report.results
    assert "500,000 pixels" in report.results
    assert "Built-Up Index Change" in report.results
    assert "+0.00430" in report.results
    assert "-2.937 °C" in report.results
    assert "Pearson Correlation" in report.results
    assert "+0.1926" in report.results
    assert "Spearman Rank Correlation" in report.results
    assert "+0.0998" in report.results
    assert "Coefficient of Fit" in report.results
    assert "0.0371" in report.results
    assert "5,000 paired pixel observations" in report.results

    # 2. Section 5 Discussion & Limitations verification
    assert "# 5. Discussion & Limitations" in report.discussion

    # 3. Section 6 Conclusion verification
    assert "# 6. Conclusion" in report.conclusion


def test_pipeline_executor_end_to_end_report_correctness() -> None:
    """Verify end-to-end PipelineExecutor generates populated, structurally coherent report.md."""
    executor = PipelineExecutor()
    context = PipelineContext(
        research_uuid="res_e2e_test",
        question="How does urban expansion affect thermal surface temperature in Hyderabad?",
        location="Hyderabad",
    )
    state = PipelineState()
    metrics = PipelineMetrics()

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir)
        res = executor.execute_pipeline(
            context=context,
            state=state,
            metrics=metrics,
            output_base_dir=out_dir,
        )

        project_dir = Path(res["project_dir"])
        report_md = project_dir / "report.md"

        assert report_md.exists()
        content = report_md.read_text(encoding="utf-8")

        # Verify DAG nodes in report
        assert "7-stage Directed Acyclic Graph" in content
        assert "node_1_planner" in content
        assert "node_7_review" in content

        # Verify non-zero runtime in report
        assert "Total Execution Time: 0.00 seconds" not in content

        # Verify spatial results in report
        assert "# 4. Results & Analysis" in content
        assert "Pearson Correlation" in content
        assert "5,000 paired pixel observations" in content

        # Verify section numbering
        assert "# 1. Introduction" in content
        assert "# 2. Related Work" in content
        assert "# 3. Data Sources & Methodology" in content
        assert "# 4. Results & Analysis" in content
        assert "# 5. Discussion & Limitations" in content
        assert "# 6. Conclusion" in content

        # Verify Git SHA in Appendix
        assert "v0.5.0-core-platform" not in content
