"""Rolling conversation dialogue memory with windowing, serialization, and search."""

from typing import Any

from src.infrastructure.llm.exceptions import MemoryError


class ConversationMemory:
    """Rolling dialogue conversation memory system."""

    def __init__(self, window_size: int = 10) -> None:
        self.window_size = window_size
        self._history: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        """Add dialogue turn."""
        if not role or not content:
            raise MemoryError("Conversation message role and content must be non-empty.")
        self._history.append({"role": role, "content": content})
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size :]

    def get_messages(self) -> list[dict[str, str]]:
        """Return list of conversation messages."""
        return list(self._history)

    def remove(self, index: int) -> dict[str, str]:
        """Remove dialogue turn by index."""
        try:
            return self._history.pop(index)
        except IndexError as err:
            raise MemoryError(f"Invalid message index {index}.") from err

    def search(self, query: str) -> list[dict[str, str]]:
        """Search dialogue turns matching query string."""
        q = query.lower()
        return [msg for msg in self._history if q in msg["content"].lower()]

    def summarize(self) -> str:
        """Summarize dialogue history."""
        return f"Conversation contains {len(self._history)} turns."

    def clear(self) -> None:
        """Clear all conversation history."""
        self._history.clear()

    def serialize(self) -> dict[str, Any]:
        """Serialize memory state to dict payload."""
        return {"window_size": self.window_size, "history": list(self._history)}

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "ConversationMemory":
        """Deserialize payload dictionary into ConversationMemory instance."""
        mem = cls(window_size=data.get("window_size", 10))
        mem._history = list(data.get("history", []))
        return mem
