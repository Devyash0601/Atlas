"""GEEPlanSpec declarative JSON execution specification schema."""

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass(frozen=True)
class GEEPlanOperation:
    """Single declarative Earth Engine operation specification."""

    op_type: str  # Declarative operation type name (e.g. LoadCollection, NDVI, Composite)
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GEEPlanSpec:
    """Immutable declarative execution plan specification."""

    plan_id: str
    target_dataset: str
    operations: list[GEEPlanOperation]
    spatial_bounds: list[float]
    temporal_range: list[str]

    @property
    def collection_id(self) -> str:
        """Alias for target_dataset for backward compatibility."""
        return self.target_dataset

    SUPPORTED_OPERATIONS: ClassVar[set[str]] = {
        "LoadCollection",
        "FilterBounds",
        "FilterDate",
        "CloudMask",
        "Composite",
        "SelectBands",
        "NDVI",
        "NDBI",
        "NDWI",
        "LST",
        "SMM",
        "WaterMask",
        "ReduceRegions",
        "Slope",
        "Elevation",
        "TimeSeries",
        "RasterStatistics",
        "ChangeDetection",
        "Export",
        "Visualization",
    }


def __getattr__(name: str) -> Any:
    """Lazy import for backward compatibility aliases to prevent circular imports."""
    if name == "PlanCompiler":
        from src.infrastructure.earth_engine_runtime.gee_plan_compiler import GEEPlanCompiler

        return GEEPlanCompiler
    if name == "PlanValidator":
        from src.infrastructure.earth_engine_runtime.gee_plan_validator import GEEPlanValidator

        return GEEPlanValidator
    if name == "PlanExecutor":
        from src.infrastructure.earth_engine_runtime.gee_executor import GEEExecutor

        return GEEExecutor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
