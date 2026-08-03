"""Task queue manager and Job interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Job:
    """Task job specification."""

    job_id: str
    task_name: str
    payload: dict[str, Any]


class TaskQueue(ABC):
    """Abstract task queue contract."""

    @abstractmethod
    async def enqueue(self, job: Job) -> None:
        """Enqueue job for async execution."""
        pass

    @abstractmethod
    async def dequeue(self) -> Job | None:
        """Dequeue next available job."""
        pass


class InMemoryTaskQueue(TaskQueue):
    """In-memory task queue implementation."""

    def __init__(self) -> None:
        self._queue: list[Job] = []

    async def enqueue(self, job: Job) -> None:
        """Add job to in-memory queue."""
        self._queue.append(job)

    async def dequeue(self) -> Job | None:
        """Pop job from queue front."""
        if not self._queue:
            return None
        return self._queue.pop(0)


class QueueManager:
    """Task queue manager aggregating background task queues."""

    def __init__(self) -> None:
        self.default_queue = InMemoryTaskQueue()
