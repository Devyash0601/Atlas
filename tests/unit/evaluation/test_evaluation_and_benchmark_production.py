"""Unit tests for Phase C Production Evaluation & Benchmark Suite."""

from pathlib import Path

from src.evaluation.benchmark_suite import BenchmarkSuite
from src.evaluation.citation_metrics import CitationMetrics
from src.evaluation.dataset_loader import BenchmarkDatasetLoader
from src.evaluation.earth_engine_metrics import EarthEngineMetricsEvaluator
from src.evaluation.hallucination_metrics import HallucinationMetrics
from src.evaluation.metrics_registry import MetricsRegistry
from src.evaluation.rag_metrics import RAGMetrics
from src.evaluation.report_metrics import ReportMetrics
from src.evaluation.runtime_metrics import RuntimeMetricsEvaluator
from src.evaluation.workflow_metrics import WorkflowMetricsEvaluator


def test_metrics_registry() -> None:
    """Verify MetricsRegistry registration and retrieval."""
    registry = MetricsRegistry()
    metric = registry.register_metric(
        name="test_metric",
        category="Test",
        description="A test metric evaluator",
        evaluator_func=lambda: 1.0,
    )
    assert metric.name == "test_metric"
    assert len(registry.get_metrics()) == 1


def test_rag_metrics_computation() -> None:
    """Verify Recall@K, MRR, and NDCG computation."""
    retrieved = ["doc_1", "doc_2", "doc_3", "doc_4", "doc_5"]
    ground_truth = {"doc_1", "doc_3"}

    res = RAGMetrics.evaluate(retrieved, ground_truth)
    assert res["recall_at_5"] == 1.0
    assert res["mrr"] == 1.0
    assert res["ndcg_at_5"] > 0.0


def test_citation_and_hallucination_metrics() -> None:
    """Verify CitationMetrics and HallucinationMetrics evaluators."""
    citations = [
        {"citation_id": "c1", "authors": ["Smith"], "doi": "10.1000/1"},
        {"citation_id": "c2", "authors": ["Doe"], "doi": ""},
    ]
    cite_res = CitationMetrics.evaluate(citations)
    assert cite_res["citation_precision"] == 1.0
    assert cite_res["doi_coverage"] == 0.5

    claims = [
        {"claim": "NDVI increases", "confidence": 0.95},
        {"claim": "LST decreases", "confidence": 0.50},
    ]
    hal_res = HallucinationMetrics.evaluate(claims)
    assert hal_res["hallucination_rate"] == 0.5
    assert hal_res["claim_support_ratio"] == 0.5


def test_workflow_ee_report_runtime_evaluators() -> None:
    """Verify Workflow, Earth Engine, Report, and Runtime metric evaluators."""
    wf_res = WorkflowMetricsEvaluator.evaluate(
        history=[{"node_id": "n1", "status": "COMPLETED", "retries": 1}],
        metrics={},
    )
    assert wf_res["workflow_completion_rate"] == 1.0
    assert wf_res["total_retries"] == 1.0

    ee_input = {"pixels_processed": 500000, "status": "COMPLETED"}
    ee_res = EarthEngineMetricsEvaluator.evaluate(ee_input)
    assert ee_res["gee_execution_success"] == 1.0
    assert ee_res["pixels_processed"] == 500000.0

    rep_input = {
        "title": "Paper",
        "abstract": "Abs",
        "introduction": "Intro",
        "results": "Res",
    }
    rep_res = ReportMetrics.evaluate(rep_input)
    assert rep_res["section_completeness"] == 1.0
    assert rep_res["reproducibility_score"] == 1.0

    run_res = RuntimeMetricsEvaluator.evaluate({"total_runtime_sec": 0.45})
    assert run_res["total_runtime_sec"] == 0.45


def test_benchmark_loader_runner_and_suite(tmp_path: Path) -> None:
    """Verify BenchmarkDatasetLoader, BenchmarkRunner, LeaderboardGenerator, and BenchmarkSuite."""
    benchmarks = BenchmarkDatasetLoader.load_default_benchmarks()
    assert len(benchmarks) >= 3

    suite = BenchmarkSuite()
    outcome = suite.run_and_export(output_dir=tmp_path)

    assert outcome["status"] == "COMPLETED"
    assert outcome["summary"]["suite_status"] == "PASSED"

    exported = outcome["exported_files"]
    assert Path(exported["json"]).exists()
    assert Path(exported["markdown"]).exists()
    assert Path(exported["html"]).exists()
    assert Path(exported["csv"]).exists()
