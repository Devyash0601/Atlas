"""StreamingEngine with token streaming, cancellation, timeout, and partial recovery."""

import asyncio
from collections.abc import AsyncGenerator

from src.infrastructure.llm.exceptions import GenerationTimeout, StreamingCancelled


class StreamingEngine:
    """Async token streaming engine with cancellation and timeout support."""

    @staticmethod
    async def stream_tokens(
        text: str,
        chunk_size: int = 4,
        timeout_seconds: float = 30.0,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[str]:
        """Stream simulated or real token chunks asynchronously."""
        words = text.split(" ")
        start_time = asyncio.get_event_loop().time()

        for i in range(0, len(words), chunk_size):
            if cancel_event and cancel_event.is_set():
                raise StreamingCancelled("Token streaming was cancelled by request.")

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout_seconds:
                raise GenerationTimeout(f"Token streaming exceeded timeout of {timeout_seconds}s.")

            chunk = " ".join(words[i : i + chunk_size]) + " "
            yield chunk
            await asyncio.sleep(0.01)
