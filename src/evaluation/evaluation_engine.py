"""EvaluationEngine orchestrating metrics computation across all 7 evaluation dimensions."""

from typing import Any

from src.evaluation.citation_metrics import CitationMetrics
from src.evaluation.earth_engine_metrics import EarthEngineMetricsEvaluator
from src.evaluation.hallucination_metrics import HallucinationMetrics
from src.evaluation.rag_metrics import RAGMetrics
from src.evaluation.report_metrics import ReportMetrics
from src.evaluation.runtime_metrics import RuntimeMetricsEvaluator
from src.evaluation.workflow_metrics import WorkflowMetricsEvaluator


class EvaluationEngine:
    """Core evaluation engine evaluating pipeline outputs against metric evaluators."""

    def evaluate_execution(
        self,
        retrieved_ids: list[str],
        ground_truth_ids: set[str],
        citations: list[dict[str, Any]],
        claims: list[dict[str, Any]],
        workflow_history: list[dict[str, Any]],
        ee_results: dict[str, Any],
        report_data: dict[str, Any],
        metrics_summary: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute complete 7-dimension evaluation report."""
        rag_res = RAGMetrics.evaluate(retrieved_ids, ground_truth_ids)
        cite_res = CitationMetrics.evaluate(citations)
        hal_res = HallucinationMetrics.evaluate(claims)
        wf_res = WorkflowMetricsEvaluator.evaluate(workflow_history, metrics_summary)
        ee_res = EarthEngineMetricsEvaluator.evaluate(ee_results)
        rep_res = ReportMetrics.evaluate(report_data)
        run_res = RuntimeMetricsEvaluator.evaluate(metrics_summary)

        combined_metrics = {
            **rag_res,
            **cite_res,
            **hal_res,
            **wf_res,
            **ee_res,
            **rep_res,
            **run_res,
        }

        overall_score = round(
            (
                combined_metrics["recall_at_5"]
                + combined_metrics["citation_precision"]
                + (1.0 - combined_metrics["hallucination_rate"])
                + combined_metrics["workflow_completion_rate"]
                + combined_metrics["gee_execution_success"]
                + combined_metrics["reproducibility_score"]
            )
            / 6.0,
            4,
        )

        return {
            "overall_score": overall_score,
            "metrics": combined_metrics,
            "passed_quality_gates": overall_score >= 0.80,
        }
