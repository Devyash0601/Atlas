"""MetricsRegistry registering and aggregating evaluation metric definitions."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class MetricDefinition:
    """Evaluation metric definition container."""

    name: str
    category: str
    description: str
    evaluator_func: Callable[..., float]
    unit: str = "ratio"


class MetricsRegistry:
    """Registry maintaining evaluation metric definitions and scores."""

    def __init__(self) -> None:
        self._metrics: dict[str, MetricDefinition] = {}

    def register_metric(
        self,
        name: str,
        category: str,
        description: str,
        evaluator_func: Callable[..., float],
        unit: str = "ratio",
    ) -> MetricDefinition:
        """Register new metric definition."""
        metric = MetricDefinition(
            name=name,
            category=category,
            description=description,
            evaluator_func=evaluator_func,
            unit=unit,
        )
        self._metrics[name] = metric
        return metric

    def get_metrics(self) -> list[MetricDefinition]:
        """Return registered metric definitions."""
        return list(self._metrics.values())
