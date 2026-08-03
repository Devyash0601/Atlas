"""4-Tier memory model: ConversationMemory, WorkflowMemory, ResearchMemory, RetrievalMemory."""

from typing import Any


class ConversationMemory:
    """Short-term dialogue context memory."""

    def __init__(self) -> None:
        self._history: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Append message to dialogue history."""
        self._history.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        """Return dialogue history."""
        return list(self._history)

    def clear(self) -> None:
        """Clear conversation history."""
        self._history.clear()


class WorkflowMemory:
    """DAG execution state memory."""

    def __init__(self) -> None:
        self._step_outputs: dict[str, Any] = {}

    def store_step_output(self, step_name: str, output: Any) -> None:
        """Store step output data."""
        self._step_outputs[step_name] = output

    def get_step_output(self, step_name: str) -> Any | None:
        """Retrieve output of completed workflow step."""
        return self._step_outputs.get(step_name)


class ResearchMemory:
    """Long-term research hypothesis and accumulated evidence memory."""

    def __init__(self) -> None:
        self.hypothesis: str = ""
        self.evidence_claims: list[dict[str, Any]] = []

    def set_hypothesis(self, hypothesis: str) -> None:
        """Set project scientific hypothesis."""
        self.hypothesis = hypothesis

    def add_evidence(self, citation: str, claim: str, confidence: float) -> None:
        """Add gathered evidence item."""
        item = {"citation": citation, "claim": claim, "confidence": confidence}
        self.evidence_claims.append(item)


class RetrievalMemory:
    """Persistent vector retrieval and cached DOI metadata memory."""

    def __init__(self) -> None:
        self._cached_chunks: dict[str, Any] = {}

    def cache_chunk(self, chunk_id: str, metadata: dict[str, Any]) -> None:
        """Cache retrieved chunk metadata."""
        self._cached_chunks[chunk_id] = metadata

    def get_cached_chunk(self, chunk_id: str) -> dict[str, Any] | None:
        """Retrieve cached chunk metadata."""
        return self._cached_chunks.get(chunk_id)
