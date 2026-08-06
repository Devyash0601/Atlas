"""WorkflowMetrics collecting execution time, parallelism, retries, and artifacts."""

from typing import Any

from src.application.workflows.research_engine.execution_history import ExecutionHistory
from src.application.workflows.research_engine.workflow_state import WorkflowState


class WorkflowMetrics:
    """Collector tracking workflow metrics and execution performance stats."""

    def __init__(self) -> None:
        self.llm_calls_count: int = 0
        self.retrieval_calls_count: int = 0
        self.ee_calls_count: int = 0

    def record_llm_call(self) -> None:
        """Increment LLM call counter."""
        self.llm_calls_count += 1

    def record_retrieval_call(self) -> None:
        """Increment retrieval call counter."""
        self.retrieval_calls_count += 1

    def record_ee_call(self) -> None:
        """Increment Earth Engine call counter."""
        self.ee_calls_count += 1

    def compute_summary(self, state: WorkflowState, history: ExecutionHistory) -> dict[str, Any]:
        """Compute execution statistics summary."""
        total_time = sum(state.node_timings.values())
        return {
            "total_nodes_count": len(state.completed_nodes) + len(state.failed_nodes),
            "completed_nodes_count": len(state.completed_nodes),
            "failed_nodes_count": len(state.failed_nodes),
            "total_execution_time_sec": round(total_time, 3),
            "total_retries_count": sum(state.retry_counts.values()),
            "produced_artifacts_count": len(state.produced_artifact_uuids),
            "llm_calls_count": self.llm_calls_count,
            "retrieval_calls_count": self.retrieval_calls_count,
            "ee_calls_count": self.ee_calls_count,
        }
