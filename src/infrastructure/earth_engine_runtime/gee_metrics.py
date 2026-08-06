"""GEEMetrics collecting execution time, pixels processed, export size, and cache statistics."""

from typing import Any


class GEEMetrics:
    """Collector tracking Earth Engine runtime performance stats."""

    def __init__(self) -> None:
        self.total_executions: int = 0
        self.total_pixels_processed: int = 0
        self.total_execution_time_sec: float = 0.0
        self.total_export_bytes: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0

    def record_execution(
        self, pixels_processed: int, duration_sec: float, cache_hit: bool = False
    ) -> None:
        """Record completed execution metrics."""
        self.total_executions += 1
        self.total_pixels_processed += pixels_processed
        self.total_execution_time_sec += duration_sec
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def record_export(self, file_size_bytes: int) -> None:
        """Record export size bytes."""
        self.total_export_bytes += file_size_bytes

    def get_stats(self) -> dict[str, Any]:
        """Return metrics summary dictionary."""
        return {
            "total_executions": self.total_executions,
            "total_pixels_processed": self.total_pixels_processed,
            "total_execution_time_sec": round(self.total_execution_time_sec, 3),
            "total_export_bytes": self.total_export_bytes,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }
