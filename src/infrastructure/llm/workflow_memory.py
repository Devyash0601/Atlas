"""Workflow execution state memory storing DAG steps and decisions."""

from typing import Any

from src.infrastructure.llm.exceptions import MemoryError


class WorkflowMemory:
    """Workflow execution state memory system."""

    def __init__(self) -> None:
        self._step_records: dict[str, dict[str, Any]] = {}

    def add(self, step_id: str, output: Any, decision: str = "success") -> None:
        """Store workflow step record."""
        if not step_id:
            raise MemoryError("Workflow step_id must not be empty.")
        self._step_records[step_id] = {"output": output, "decision": decision}

    def remove(self, step_id: str) -> None:
        """Remove workflow step record."""
        if step_id not in self._step_records:
            raise MemoryError(f"Workflow step '{step_id}' not found.")
        del self._step_records[step_id]

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search workflow step records matching query string."""
        q = query.lower()
        return [
            {"step_id": k, **v}
            for k, v in self._step_records.items()
            if q in k.lower() or q in str(v).lower()
        ]

    def summarize(self) -> str:
        """Summarize workflow execution history."""
        return f"Workflow recorded {len(self._step_records)} execution steps."

    def clear(self) -> None:
        """Clear all workflow memory."""
        self._step_records.clear()

    def serialize(self) -> dict[str, Any]:
        """Serialize workflow memory state to dict."""
        return {"step_records": dict(self._step_records)}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "WorkflowMemory":
        """Deserialize data dict into WorkflowMemory instance."""
        mem = cls()
        mem._step_records = dict(data.get("step_records", {}))
        return mem
