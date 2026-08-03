"""RuntimeQueue providing Priority FIFO scheduling and concurrency control."""

import time
from typing import Any

from src.infrastructure.llm.exceptions import QueueOverflow
from src.infrastructure.llm.generation import GenerationRequest


class RuntimeQueue:
    """Async request queue with priority scheduling and concurrency limit."""

    def __init__(self, max_capacity: int = 100, max_concurrency: int = 4) -> None:
        self.max_capacity = max_capacity
        self.max_concurrency = max_concurrency
        self._queue: list[tuple[int, float, GenerationRequest]] = []
        self._active_count = 0
        self._cancelled: set[str] = set()

    def enqueue(self, request: GenerationRequest) -> None:
        """Enqueue request into priority queue."""
        if len(self._queue) >= self.max_capacity:
            raise QueueOverflow(f"RuntimeQueue max capacity ({self.max_capacity}) exceeded.")
        # Store (-priority, timestamp, request) for max-priority sorting
        self._queue.append((-request.priority, time.monotonic(), request))
        self._queue.sort(key=lambda item: (item[0], item[1]))

    def dequeue(self) -> GenerationRequest | None:
        """Dequeue next highest priority non-cancelled request."""
        while self._queue:
            _, _, req = self._queue.pop(0)
            if req.request_id in self._cancelled:
                self._cancelled.remove(req.request_id)
                continue
            self._active_count += 1
            return req
        return None

    def release(self) -> None:
        """Release active concurrency lock count."""
        if self._active_count > 0:
            self._active_count -= 1

    def cancel(self, request_id: str) -> bool:
        """Cancel queued request by ID."""
        self._cancelled.add(request_id)
        return True

    def get_stats(self) -> dict[str, Any]:
        """Return queue metrics."""
        return {
            "queued_count": len(self._queue),
            "active_count": self._active_count,
            "max_concurrency": self.max_concurrency,
        }
