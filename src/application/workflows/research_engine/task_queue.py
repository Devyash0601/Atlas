"""TaskQueue managing async task execution list for workflow nodes."""

from typing import Any

from src.application.workflows.research_engine.workflow_graph import WorkflowNode


class TaskQueue:
    """Task queue container for pending workflow nodes."""

    def __init__(self) -> None:
        self._queue: list[WorkflowNode] = []

    def push(self, node: WorkflowNode) -> None:
        """Push node onto queue."""
        self._queue.append(node)

    def pop(self) -> WorkflowNode | None:
        """Pop next node from queue."""
        return self._queue.pop(0) if self._queue else None

    def is_empty(self) -> bool:
        """Return True if queue is empty."""
        return len(self._queue) == 0

    def get_stats(self) -> dict[str, Any]:
        """Return task queue statistics."""
        return {"queued_tasks_count": len(self._queue)}
