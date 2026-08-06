"""GEERuntime unified facade managing Earth Engine workspace operations."""

from typing import Any

from src.infrastructure.earth_engine_runtime.analysis import GEEStatisticsEngine
from src.infrastructure.earth_engine_runtime.catalog import GEEDatasetCatalog
from src.infrastructure.earth_engine_runtime.gee_client import GEEClient
from src.infrastructure.earth_engine_runtime.gee_executor import GEEExecutor
from src.infrastructure.earth_engine_runtime.gee_export_manager import GEEExportManager
from src.infrastructure.earth_engine_runtime.gee_metrics import GEEMetrics
from src.infrastructure.earth_engine_runtime.gee_plan_compiler import GEEPlanCompiler
from src.infrastructure.earth_engine_runtime.gee_plan_validator import GEEPlanValidator
from src.infrastructure.earth_engine_runtime.gee_result_processor import GEEResultProcessor
from src.infrastructure.earth_engine_runtime.gee_visualization import GEEVisualizationEngine
from src.infrastructure.earth_engine_runtime.plan_spec import GEEPlanSpec
from src.infrastructure.earth_engine_runtime.tasks import GEETaskManager


class GEERuntime:
    """Unified runtime engine for Earth Engine workspace operations."""

    def __init__(self) -> None:
        self.client = GEEClient()
        self.catalog = GEEDatasetCatalog()
        self.validator = GEEPlanValidator(self.catalog)
        self.compiler = GEEPlanCompiler()
        self.executor = GEEExecutor(self.validator, self.compiler)
        self.task_manager = GEETaskManager()
        self.statistics_engine = GEEStatisticsEngine()
        self.visualization_engine = GEEVisualizationEngine()
        self.export_manager = GEEExportManager()
        self.result_processor = GEEResultProcessor()
        self.metrics = GEEMetrics()

    def initialize(self) -> bool:
        """Initialize GEE client runtime."""
        return self.client.initialize()

    def execute_plan(self, plan: GEEPlanSpec) -> dict[str, Any]:
        """Validate, compile, execute plan, and record metrics."""
        self.initialize()
        raw_output = self.executor.execute(plan)
        artifact = self.result_processor.process_execution_output(raw_output)

        self.metrics.record_execution(
            pixels_processed=raw_output.get("pixels_processed", 0),
            duration_sec=raw_output.get("duration_sec", 0.0),
        )

        return {
            "raw_output": raw_output,
            "result_artifact": artifact,
        }

    def check_health(self) -> dict[str, Any]:
        """Return runtime health status."""
        return self.client.check_health()
