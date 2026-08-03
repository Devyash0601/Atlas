"""Research memory storing scientific hypotheses, extracted facts, and paper references."""

from typing import Any

from src.infrastructure.llm.exceptions import MemoryError


class ResearchMemory:
    """Long-term research memory storing hypotheses and extracted facts."""

    def __init__(self) -> None:
        self.hypothesis: str = ""
        self._facts: list[dict[str, Any]] = []

    def set_hypothesis(self, hypothesis: str) -> None:
        """Set primary research hypothesis."""
        self.hypothesis = hypothesis

    def add(self, fact_id: str, fact_text: str, source_doi: str) -> None:
        """Add extracted scientific fact."""
        if not fact_id or not fact_text:
            raise MemoryError("Research fact_id and fact_text must not be empty.")
        self._facts.append({"fact_id": fact_id, "text": fact_text, "doi": source_doi})

    def remove(self, fact_id: str) -> None:
        """Remove extracted fact by ID."""
        initial_len = len(self._facts)
        self._facts = [f for f in self._facts if f["fact_id"] != fact_id]
        if len(self._facts) == initial_len:
            raise MemoryError(f"Fact '{fact_id}' not found.")

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search extracted facts matching query string."""
        q = query.lower()
        return [f for f in self._facts if q in f["text"].lower() or q in f["doi"].lower()]

    def summarize(self) -> str:
        """Summarize research memory state."""
        return f"Hypothesis: '{self.hypothesis}'. Facts stored: {len(self._facts)}."

    def clear(self) -> None:
        """Clear research memory."""
        self.hypothesis = ""
        self._facts.clear()

    def serialize(self) -> dict[str, Any]:
        """Serialize research memory to dictionary."""
        return {"hypothesis": self.hypothesis, "facts": list(self._facts)}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "ResearchMemory":
        """Deserialize payload dictionary into ResearchMemory instance."""
        mem = cls()
        mem.hypothesis = data.get("hypothesis", "")
        mem._facts = list(data.get("facts", []))
        return mem
