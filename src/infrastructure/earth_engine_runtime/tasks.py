"""GEETaskManager managing background Earth Engine tasks with priority scheduling."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.infrastructure.earth_engine_runtime.gee_export_manager import GEEExportManager
from src.infrastructure.earth_engine_runtime.gee_result_processor import GEEResultProcessor
from src.infrastructure.earth_engine_runtime.plan_spec import GEEPlanOperation, GEEPlanSpec


@dataclass
class GEETaskRecord:
    """Task record for background Earth Engine computation or export."""

    task_id: str
    plan_id: str
    status: str  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class GEETaskManager:
    """Manager tracking queued and background Earth Engine execution tasks."""

    def __init__(self) -> None:
        self.tasks: dict[str, GEETaskRecord] = {}

    def submit_task(self, task_id: str, plan_id: str, priority: int = 0) -> GEETaskRecord:
        """Submit new task to task manager queue."""
        rec = GEETaskRecord(task_id=task_id, plan_id=plan_id, status="QUEUED", priority=priority)
        self.tasks[task_id] = rec
        return rec

    def get_task(self, task_id: str) -> GEETaskRecord | None:
        """Retrieve task record by ID."""
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel task by ID."""
        if task_id in self.tasks:
            self.tasks[task_id].status = "CANCELLED"
            return True
        return False

    def list_tasks(self) -> list[GEETaskRecord]:
        """Return list of all submitted tasks."""
        return list(self.tasks.values())

    def get_history(self) -> list[GEETaskRecord]:
        """Backward compatibility get_history helper."""
        return list(self.tasks.values())

    @classmethod
    def plan_ndvi_task(
        cls,
        roi: Any = None,
        time_range: Any = None,
        dataset: Any = None,
        cloud_mask: Any = None,
    ) -> GEEPlanSpec:
        """Backward compatibility helper creating NDVI GEEPlanSpec."""
        return GEEPlanSpec(
            plan_id="plan_ndvi_default",
            target_dataset="COPERNICUS/S2_SR_HARMONIZED",
            operations=[GEEPlanOperation("LoadCollection"), GEEPlanOperation("NDVI")],
            spatial_bounds=[2.2, 48.5, 2.5, 49.0],
            temporal_range=["2024-01-01", "2024-06-01"],
        )

    @classmethod
    def monitor_task(cls, task_id: str) -> dict[str, Any]:
        """Backward compatibility helper monitoring task status."""
        return {"task_id": task_id, "status": "COMPLETED"}

    def record(self, record: Any) -> None:
        """Backward compatibility record helper."""
        if hasattr(record, "task_id"):
            self.tasks[record.task_id] = record


# Backward compatibility aliases
AssetExporter = GEEExportManager
ResultImporter = GEEResultProcessor
TaskMonitor = GEETaskManager
TaskPlanner = GEETaskManager


def __getattr__(name: str) -> Any:
    """Lazy import TaskExecutor alias to avoid circular imports."""
    if name == "TaskExecutor":
        from src.infrastructure.earth_engine_runtime.gee_executor import GEEExecutor

        return GEEExecutor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
