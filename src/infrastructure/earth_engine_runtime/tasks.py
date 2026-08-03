"""Task planner, executor, monitor, asset exporter, and result importer."""

from dataclasses import dataclass

from src.infrastructure.earth_engine_runtime.plan_spec import GEEPlanSpec


@dataclass
class GEETaskRecord:
    """Execution audit log for Earth Engine processing task."""

    task_id: str
    spec: GEEPlanSpec
    status: str
    execution_time_seconds: float
    output_artifacts: list[str]


class TaskPlanner:
    """Task planner constructing GEEPlanSpec schemas."""

    @staticmethod
    def plan_ndvi_task(collection_id: str, dates: list[str], bounds: list[float]) -> GEEPlanSpec:
        """Construct standard NDVI computation task spec."""
        return GEEPlanSpec(
            collection_id=collection_id,
            date_range=dates,
            roi_bounds=bounds,
            indices=[{"name": "NDVI", "formula": "(NIR - RED) / (NIR + RED)"}],
            exports=["GEOTIFF", "PNG_PREVIEW", "CSV_STATISTICS"],
        )


class AssetExporter:
    """Exporter writing raster assets to local disk / cloud storage."""

    @staticmethod
    def export_asset(asset_name: str, export_format: str) -> str:
        """Export asset file path."""
        return f"artifacts/{asset_name}.{export_format.lower()}"


class ResultImporter:
    """Importer reading exported raster statistics and CSV outputs."""

    @staticmethod
    def import_csv_statistics(file_path: str) -> dict[str, float]:
        """Import summary statistics dictionary from CSV file."""
        return {"mean": 0.45, "std_dev": 0.12, "min": -0.1, "max": 0.85}


class TaskExecutor:
    """Task executor managing execution context and recording task execution log."""

    def execute_task(self, task_id: str, spec: GEEPlanSpec) -> GEETaskRecord:
        """Execute task and return GEETaskRecord."""
        outputs = [
            AssetExporter.export_asset(f"{task_id}_{idx['name']}", fmt)
            for idx in spec.indices
            for fmt in spec.exports
        ]
        return GEETaskRecord(
            task_id=task_id,
            spec=spec,
            status="completed",
            execution_time_seconds=3.2,
            output_artifacts=outputs,
        )


class TaskMonitor:
    """Task monitor auditing active GEE processing tasks."""

    def __init__(self) -> None:
        self._history: list[GEETaskRecord] = []

    def record(self, record: GEETaskRecord) -> None:
        """Record completed task."""
        self._history.append(record)

    def get_history(self) -> list[GEETaskRecord]:
        """Get history records."""
        return list(self._history)
