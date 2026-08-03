"""RuntimeMetrics tracking inference latency, tokens, failures, and RAM."""

from typing import Any


class RuntimeMetrics:
    """Collector tracking inference statistics and performance metrics."""

    def __init__(self) -> None:
        self.total_requests: int = 0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_latency_seconds: float = 0.0
        self.total_retries: int = 0
        self.total_failures: int = 0

    def record_generation(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        latency_seconds: float,
        retries: int = 0,
    ) -> None:
        """Record completed generation stats."""
        self.total_requests += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_latency_seconds += latency_seconds
        self.total_retries += retries

    def record_failure(self) -> None:
        """Record generation failure count."""
        self.total_failures += 1

    def get_stats(self) -> dict[str, Any]:
        """Return metrics summary dictionary."""
        avg_tokens_per_sec = (
            round(self.total_completion_tokens / self.total_latency_seconds, 2)
            if self.total_latency_seconds > 0
            else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "avg_tokens_per_second": avg_tokens_per_sec,
            "total_retries": self.total_retries,
            "total_failures": self.total_failures,
        }
