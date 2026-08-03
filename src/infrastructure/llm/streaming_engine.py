"""Streaming engine yielding tokens from LLM inference async streams."""

from collections.abc import AsyncGenerator


class StreamingEngine:
    """Async generator streaming engine for local LLM token generation."""

    @staticmethod
    async def stream_tokens(text: str, chunk_size: int = 4) -> AsyncGenerator[str]:
        """Stream simulated token chunks for LLM output."""
        words = text.split(" ")
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size]) + " "
            yield chunk
