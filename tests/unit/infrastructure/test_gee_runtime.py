"""Unit tests for Earth Engine Runtime (Connection, Catalog, PlanSpec, Tasks, Analysis)."""

import pytest

from src.infrastructure.earth_engine_runtime.analysis import StatisticsEngine, VisualizationEngine
from src.infrastructure.earth_engine_runtime.catalog import DatasetCatalog
from src.infrastructure.earth_engine_runtime.connection import (
    GEEAuthenticator,
    GEEConnectionManager,
)
from src.infrastructure.earth_engine_runtime.plan_spec import (
    PlanCompiler,
    PlanExecutor,
    PlanValidator,
)
from src.infrastructure.earth_engine_runtime.tasks import (
    AssetExporter,
    ResultImporter,
    TaskExecutor,
    TaskMonitor,
    TaskPlanner,
)


def test_gee_connection_and_catalog() -> None:
    """Verify GEE ConnectionManager and DatasetCatalog."""
    auth = GEEAuthenticator(service_account="test@gee", key_file="key.json")
    conn = GEEConnectionManager(auth)
    assert conn.initialize() is True

    status = conn.get_status()
    assert status["authenticated"] is True

    ds = DatasetCatalog.get_dataset("landsat_c2")
    assert ds.satellite == "Landsat 8/9"

    with pytest.raises(KeyError):
        DatasetCatalog.get_dataset("unknown_alias")


def test_gee_plan_spec_validation_compilation() -> None:
    """Verify GEEPlanSpec validation and compilation."""
    valid_dict = {
        "collection_id": "LANDSAT/LC08/C02/T1_L2",
        "date_range": ["2024-01-01", "2024-12-31"],
        "roi_bounds": [2.2, 48.5, 2.5, 49.0],
        "indices": [{"name": "NDVI", "formula": "(B5-B4)/(B5+B4)"}],
        "exports": ["GEOTIFF", "PNG_PREVIEW"],
    }
    PlanValidator.validate(valid_dict)
    spec = PlanCompiler.compile(valid_dict)
    assert spec.collection_id == "LANDSAT/LC08/C02/T1_L2"

    executor = PlanExecutor(None)
    res = executor.execute_plan(spec)
    assert res["status"] == "success"

    # Invalid bounding box
    invalid_bounds_dict = dict(valid_dict)
    invalid_bounds_dict["roi_bounds"] = [2.5, 48.5, 2.2, 49.0]
    with pytest.raises(ValueError):
        PlanValidator.validate(invalid_bounds_dict)


def test_gee_task_execution_and_analysis() -> None:
    """Verify GEE Task execution, StatisticsEngine, and VisualizationEngine."""
    spec = TaskPlanner.plan_ndvi_task(
        "LANDSAT/LC08/C02/T1_L2",
        ["2024-01-01", "2024-06-01"],
        [2.0, 48.0, 3.0, 49.0],
    )
    executor = TaskExecutor()
    record = executor.execute_task("task_001", spec)
    assert record.status == "completed"

    monitor = TaskMonitor()
    monitor.record(record)
    assert len(monitor.get_history()) == 1

    # Analysis statistics calculation
    nir = [0.4, 0.5, 0.6]
    red = [0.1, 0.15, 0.2]
    stats = StatisticsEngine.calculate_ndvi_stats(nir, red)
    assert stats.index_name == "NDVI"
    assert stats.mean_val > 0.0

    st_b10 = [30000.0, 31000.0]
    lst_celsius = StatisticsEngine.calculate_lst_celsius(st_b10)
    assert len(lst_celsius) == 2

    palette = VisualizationEngine.get_palette_for_index("NDVI")
    assert len(palette) > 0

    assert "artifacts/" in AssetExporter.export_asset("test_asset", "GEOTIFF")
    imported_stats = ResultImporter.import_csv_statistics("dummy.csv")
    assert "mean" in imported_stats
