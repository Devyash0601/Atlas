"""WorkflowMetricsEvaluator measuring DAG completion, node failures, and retries."""

from typing import Any


class WorkflowMetricsEvaluator:
    """Evaluator computing workflow execution metrics."""

    @staticmethod
    def evaluate(history: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, float]:
        """Compute workflow completion and retry metrics."""
        total_nodes = len(history)
        if total_nodes == 0:
            return {
                "workflow_completion_rate": 1.0,
                "node_failure_rate": 0.0,
                "total_retries": 0.0,
            }

        completed = sum(1 for item in history if item.get("status") == "COMPLETED")
        failed = total_nodes - completed
        total_retries = sum(item.get("retries", 0) for item in history)

        return {
            "workflow_completion_rate": round(completed / total_nodes, 4),
            "node_failure_rate": round(failed / total_nodes, 4),
            "total_retries": float(total_retries),
        }
