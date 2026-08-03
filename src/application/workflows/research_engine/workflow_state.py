"""WorkflowState tracking current, completed, failed, pending, and running nodes."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowState:
    """State tracking container for workflow execution."""

    workflow_id: str
    status: str = "PENDING"  # PENDING, RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED
    current_node: str | None = None
    completed_nodes: list[str] = field(default_factory=list)
    failed_nodes: list[str] = field(default_factory=list)
    pending_nodes: list[str] = field(default_factory=list)
    running_nodes: list[str] = field(default_factory=list)
    retry_counts: dict[str, int] = field(default_factory=dict)
    node_timings: dict[str, float] = field(default_factory=dict)
    overall_confidence: float = 1.0
    produced_artifact_uuids: list[str] = field(default_factory=list)

    def mark_running(self, node_id: str) -> None:
        """Mark node as currently running."""
        if node_id in self.pending_nodes:
            self.pending_nodes.remove(node_id)
        if node_id not in self.running_nodes:
            self.running_nodes.append(node_id)
        self.current_node = node_id

    def mark_completed(self, node_id: str, duration_sec: float) -> None:
        """Mark node as successfully completed."""
        if node_id in self.running_nodes:
            self.running_nodes.remove(node_id)
        if node_id not in self.completed_nodes:
            self.completed_nodes.append(node_id)
        self.node_timings[node_id] = duration_sec

    def mark_failed(self, node_id: str) -> None:
        """Mark node as failed and increment retry count."""
        if node_id in self.running_nodes:
            self.running_nodes.remove(node_id)
        if node_id not in self.failed_nodes:
            self.failed_nodes.append(node_id)
        self.retry_counts[node_id] = self.retry_counts.get(node_id, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize state object to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": list(self.completed_nodes),
            "failed_nodes": list(self.failed_nodes),
            "pending_nodes": list(self.pending_nodes),
            "running_nodes": list(self.running_nodes),
            "retry_counts": dict(self.retry_counts),
            "node_timings": dict(self.node_timings),
            "overall_confidence": self.overall_confidence,
            "produced_artifact_uuids": list(self.produced_artifact_uuids),
        }
