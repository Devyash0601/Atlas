"""ExecutionHistory tracking node executions for replayability and auditing."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ExecutionRecord:
    """Audit record for a single node execution."""

    record_id: str
    node_id: str
    task_type: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    duration_sec: float
    status: str  # SUCCESS, FAILED
    error_message: str | None = None
    retry_count: int = 0
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


class ExecutionHistory:
    """Auditable, replayable execution history store."""

    def __init__(self) -> None:
        self.records: list[ExecutionRecord] = []

    def record_execution(
        self,
        record_id: str,
        node_id: str,
        task_type: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        duration_sec: float,
        status: str = "SUCCESS",
        error_message: str | None = None,
        retry_count: int = 0,
    ) -> ExecutionRecord:
        """Record node execution attempt in history."""
        rec = ExecutionRecord(
            record_id=record_id,
            node_id=node_id,
            task_type=task_type,
            inputs=inputs,
            outputs=outputs,
            duration_sec=duration_sec,
            status=status,
            error_message=error_message,
            retry_count=retry_count,
        )
        self.records.append(rec)
        return rec

    def get_history_for_node(self, node_id: str) -> list[ExecutionRecord]:
        """Return execution records for specific node."""
        return [r for r in self.records if r.node_id == node_id]

    def count(self) -> int:
        """Return total execution record count."""
        return len(self.records)
