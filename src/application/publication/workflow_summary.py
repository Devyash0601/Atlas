"""WorkflowSummaryGenerator formatting DAG topology, execution timeline, runtime, and retries."""

from typing import Any


class WorkflowSummaryGenerator:
    """Generator constructing deterministic workflow summary sections for research papers."""

    @staticmethod
    def generate_workflow_summary(history: list[dict[str, Any]], metrics: dict[str, Any]) -> str:
        """Generate structured Workflow Summary section."""
        total_nodes = len(history)
        total_retries = sum(item.get("retries", 0) for item in history)
        total_time = metrics.get("total_execution_time_sec", 0.0)

        lines: list[str] = [
            "### Workflow Methodology & DAG Execution",
            (
                f"The research pipeline executed an autonomous 7-stage Directed Acyclic Graph "
                f"(DAG) workflow containing **{total_nodes} nodes**."
            ),
            f"- **Total Execution Time**: {total_time:.2f} seconds",
            f"- **Execution Retries**: {total_retries}",
            "- **State Artifact Passings**: Immutable versioned artifact store",
            "\n#### Executed Workflow Pipeline Stages:",
        ]

        for idx, step in enumerate(history, 1):
            node_id = step.get("node_id", f"node_{idx}")
            task_type = step.get("task_type", "Task")
            status = step.get("status", "COMPLETED")
            duration = step.get("duration_sec", 0.0)
            lines.append(f"{idx}. **{node_id}** (`{task_type}`): {status} ({duration:.3f}s)")

        return "\n".join(lines)
