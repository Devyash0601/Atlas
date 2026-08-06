"""Unit tests for Sprint 4 Production Earth Engine Execution Engine Subsystem."""

from pathlib import Path

import pytest

from src.infrastructure.earth_engine_runtime.analysis import GEEStatisticsEngine
from src.infrastructure.earth_engine_runtime.catalog import GEEDatasetCatalog
from src.infrastructure.earth_engine_runtime.gee_authenticator import GEEAuthenticator
from src.infrastructure.earth_engine_runtime.gee_client import GEEClient
from src.infrastructure.earth_engine_runtime.gee_error_handler import (
    EarthEngineError,
    EEAuthenticationError,
    EECompilationError,
    EEDatasetUnavailable,
    EEExecutionError,
    EEExportError,
    EEPlanValidationError,
    EEQuotaExceeded,
    EERetryLimitExceeded,
    EETimeoutError,
)
from src.infrastructure.earth_engine_runtime.gee_executor import GEEExecutor
from src.infrastructure.earth_engine_runtime.gee_export_manager import GEEExportManager
from src.infrastructure.earth_engine_runtime.gee_metrics import GEEMetrics
from src.infrastructure.earth_engine_runtime.gee_plan_compiler import GEEPlanCompiler
from src.infrastructure.earth_engine_runtime.gee_plan_validator import GEEPlanValidator
from src.infrastructure.earth_engine_runtime.gee_runtime import GEERuntime
from src.infrastructure.earth_engine_runtime.gee_visualization import GEEVisualizationEngine
from src.infrastructure.earth_engine_runtime.plan_spec import (
    GEEPlanOperation,
    GEEPlanSpec,
)
from src.infrastructure.earth_engine_runtime.tasks import GEETaskManager


def test_gee_authenticator_and_client() -> None:
    """Verify GEEAuthenticator authentication modes, token refresh, and GEEClient health checks."""
    auth = GEEAuthenticator(mode="service_account", project_id="test_project")
    assert auth.authenticate() is True
    auth.validate_connection()
    auth._token_expiry_timestamp = 0.0
    auth.refresh_token_if_needed()

    status = auth.get_status()
    assert status["is_authenticated"] is True
    assert status["project_id"] == "test_project"

    client = GEEClient(authenticator=auth)
    assert client.initialize() is True
    health = client.check_health()
    assert health["status"] == "healthy"


def test_gee_dataset_catalog() -> None:
    """Verify GEEDatasetCatalog dataset metadata discovery and error handling."""
    catalog = GEEDatasetCatalog()
    s2 = catalog.get_dataset("COPERNICUS/S2_SR_HARMONIZED")
    assert s2.resolution_meters == 10.0
    assert "NDVI" in s2.recommended_indices

    assert len(catalog.list_datasets()) == 6

    with pytest.raises(EEDatasetUnavailable):
        catalog.get_dataset("INVALID/DATASET/ASSET")


def test_gee_plan_validator_and_compiler() -> None:
    """Verify GEEPlanValidator validation rules and deterministic GEEPlanCompiler outputs."""
    catalog = GEEDatasetCatalog()
    validator = GEEPlanValidator(catalog)
    compiler = GEEPlanCompiler()

    plan = GEEPlanSpec(
        plan_id="plan_001",
        target_dataset="COPERNICUS/S2_SR_HARMONIZED",
        operations=[
            GEEPlanOperation("LoadCollection"),
            GEEPlanOperation("FilterBounds", {"bounds": [2.2, 48.5, 2.5, 49.0]}),
            GEEPlanOperation("FilterDate", {"start": "2024-01-01", "end": "2024-06-01"}),
            GEEPlanOperation("NDVI"),
            GEEPlanOperation("RasterStatistics"),
        ],
        spatial_bounds=[2.2, 48.5, 2.5, 49.0],
        temporal_range=["2024-01-01", "2024-06-01"],
    )

    assert validator.validate_plan(plan) is True

    compiled = compiler.compile_plan(plan)
    assert compiled["plan_id"] == "plan_001"
    assert len(compiled["compiled_call_tree"]) == 5

    # Invalid geometry bounds check
    invalid_plan = GEEPlanSpec(
        plan_id="inv_1",
        target_dataset="COPERNICUS/S2_SR_HARMONIZED",
        operations=[],
        spatial_bounds=[2.2, 48.5],
        temporal_range=["2024-01-01", "2024-06-01"],
    )
    with pytest.raises(EEPlanValidationError):
        validator.validate_plan(invalid_plan)

    # Invalid temporal range check
    invalid_time_plan = GEEPlanSpec(
        plan_id="inv_2",
        target_dataset="COPERNICUS/S2_SR_HARMONIZED",
        operations=[],
        spatial_bounds=[2.2, 48.5, 2.5, 49.0],
        temporal_range=["2024-01-01"],
    )
    with pytest.raises(EEPlanValidationError):
        validator.validate_plan(invalid_time_plan)

    # Invalid operation check
    invalid_op_plan = GEEPlanSpec(
        plan_id="inv_3",
        target_dataset="COPERNICUS/S2_SR_HARMONIZED",
        operations=[GEEPlanOperation("UnsupportedOp")],
        spatial_bounds=[2.2, 48.5, 2.5, 49.0],
        temporal_range=["2024-01-01", "2024-06-01"],
    )
    with pytest.raises(EEPlanValidationError):
        validator.validate_plan(invalid_op_plan)


def test_gee_executor_task_manager_and_metrics() -> None:
    """Verify GEEExecutor execution flows, GEETaskManager tracking, and GEEMetrics counters."""
    executor = GEEExecutor()
    plan = GEEPlanSpec(
        plan_id="plan_002",
        target_dataset="LANDSAT/LC08/C02/T1_L2",
        operations=[GEEPlanOperation("LoadCollection"), GEEPlanOperation("LST")],
        spatial_bounds=[2.2, 48.5, 2.5, 49.0],
        temporal_range=["2024-01-01", "2024-06-01"],
    )

    result = executor.execute(plan)
    assert result["status"] == "COMPLETED"
    assert isinstance(result["result_summary"]["mean_lst_celsius"], float)
    assert result["pixels_processed"] > 0

    task_mgr = GEETaskManager()
    task_rec = task_mgr.submit_task("task_1", "plan_002", priority=5)
    assert task_rec.status == "QUEUED"
    assert task_mgr.get_task("task_1") is not None
    assert task_mgr.cancel_task("task_1") is True
    assert task_mgr.cancel_task("invalid_task_id") is False
    assert task_mgr.get_task("task_1").status == "CANCELLED"
    assert len(task_mgr.list_tasks()) == 1

    metrics = GEEMetrics()
    metrics.record_execution(pixels_processed=1000, duration_sec=1.2, cache_hit=True)
    metrics.record_export(512)
    stats = metrics.get_stats()
    assert stats["total_executions"] == 1
    assert stats["cache_hits"] == 1
    assert stats["total_export_bytes"] == 512


def test_gee_statistics_and_visualization_engines() -> None:
    """Verify GEEStatisticsEngine reductions and GEEVisualizationEngine color palettes."""
    stats_engine = GEEStatisticsEngine()
    raster_stats = stats_engine.compute_raster_statistics([0.2, 0.4, 0.6, 0.8])
    assert raster_stats.mean == 0.5
    assert raster_stats.min_val == 0.2
    assert raster_stats.max_val == 0.8

    ts = stats_engine.compute_time_series(2020, 2022)
    assert len(ts) == 3

    vis_engine = GEEVisualizationEngine()
    ndvi_vis = vis_engine.create_ndvi_visualization()
    lst_vis = vis_engine.create_lst_heatmap()

    assert "NDVI" in ndvi_vis.layer_name
    assert "LST" in lst_vis.layer_name
    assert len(ndvi_vis.color_palette) > 0


def test_export_manager_result_processor_and_runtime(tmp_path: Path) -> None:
    """Verify GEEExportManager, GEEResultProcessor, and GEERuntime facade."""
    export_mgr = GEEExportManager()
    artifact = export_mgr.export_dataset(
        export_id="exp_001",
        export_format="GeoTIFF",
        destination_dir=tmp_path,
        content_data=b"Binary raster export content",
    )

    assert artifact.file_size_bytes > 0
    assert len(artifact.checksum_sha256) == 64

    runtime = GEERuntime()
    assert runtime.initialize() is True

    plan = GEEPlanSpec(
        plan_id="plan_003",
        target_dataset="COPERNICUS/S2_SR_HARMONIZED",
        operations=[GEEPlanOperation("LoadCollection"), GEEPlanOperation("NDVI")],
        spatial_bounds=[2.2, 48.5, 2.5, 49.0],
        temporal_range=["2024-01-01", "2024-06-01"],
    )

    outcome = runtime.execute_plan(plan)
    assert outcome["raw_output"]["status"] == "COMPLETED"
    assert outcome["result_artifact"].target_dataset == "COPERNICUS/S2_SR_HARMONIZED"
    assert runtime.check_health()["status"] == "healthy"


def test_typed_exceptions_instantiation() -> None:
    """Verify typed GEE runtime exception inheritance tree."""
    errs = [
        EarthEngineError("base"),
        EEAuthenticationError("auth"),
        EEDatasetUnavailable("dataset"),
        EEPlanValidationError("plan"),
        EECompilationError("compilation"),
        EEExecutionError("execution"),
        EEExportError("export"),
        EETimeoutError("timeout"),
        EEQuotaExceeded("quota"),
        EERetryLimitExceeded("retry"),
    ]
    assert len(errs) == 10
    for e in errs:
        assert isinstance(e, EarthEngineError)
