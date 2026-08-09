"""Unit and API integration tests for GEE Tile Services & Change Analysis.

All tests mock ee.Initialize() and ee API calls so they run without
real GEE credentials. Live verification is done separately.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.earth_engine_runtime.exceptions import (
    InvalidROIError,
)
from src.infrastructure.earth_engine_runtime.types import TileRequest

# Modules where `ee` is imported and needs patching
_EE_PATCH_TARGETS = [
    "src.infrastructure.earth_engine_runtime.gee_authenticator.ee",
    "src.infrastructure.earth_engine_runtime.gee_service.ee",
    "src.infrastructure.earth_engine_runtime.tile_service.ee",
]


# ── Helpers ─────────────────────────────────────────────────


def _build_mocked_ee() -> MagicMock:
    """Create a fully-mocked ee module for testing."""
    mock_ee = MagicMock()
    mock_ee.ServiceAccountCredentials.return_value = MagicMock()
    mock_ee.Initialize.return_value = None

    mock_geom = MagicMock()
    mock_ee.Geometry.Rectangle.return_value = mock_geom

    mock_tile_fetcher = MagicMock()
    mock_tile_fetcher.url_format = "https://earthengine.googleapis.com/v1/projects/earthengine-legacy/maps/test_hash/tiles/{z}/{x}/{y}"

    mock_samples = MagicMock()
    mock_samples.getInfo.return_value = {
        "features": [
            {"properties": {"delta_ndbi": 0.005 * i, "delta_lst": 0.2 * i - 1.0}}
            for i in range(1, 101)
        ]
    }

    mock_image = MagicMock()
    mock_image.getMapId.return_value = {
        "mapid": "projects/earthengine-legacy/maps/test_hash",
        "token": "tok_test_hash",
        "tile_fetcher": mock_tile_fetcher,
    }
    mock_image.subtract.return_value = mock_image
    mock_image.resample.return_value.reproject.return_value = mock_image
    mock_image.mask.return_value.And.return_value = mock_image
    mock_image.updateMask.return_value = mock_image
    mock_image.sample.return_value = mock_samples

    mock_collection = MagicMock()
    mock_collection.filterBounds.return_value = mock_collection
    mock_collection.filterDate.return_value = mock_collection
    mock_collection.filter.return_value = mock_collection
    mock_collection.merge.return_value = mock_collection
    mock_collection.map.return_value = mock_collection
    mock_clip = mock_collection.select.return_value.median.return_value
    mock_clip.clip.return_value = mock_image
    mock_clip.normalizedDifference.return_value.clip.return_value = mock_image
    mock_collection.median.return_value.clip.return_value = mock_image
    mock_ee.ImageCollection.return_value = mock_collection
    mock_ee.Image.return_value = mock_image
    mock_ee.Filter.lte.return_value = MagicMock()

    class FakeEEImage:
        def __init__(self, *args, **kwargs):
            pass

        def rename(self, *args, **kwargs):
            return mock_image

        def updateMask(self, *args, **kwargs):
            return mock_image

        def mask(self, *args, **kwargs):
            return mock_image

        def resample(self, *args, **kwargs):
            return mock_image

    mock_ee.Image = FakeEEImage
    return mock_ee


# ── Fixtures ────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_gee_state():  # type: ignore[no-untyped-def]
    """Reset GEEAuthenticator class-level state between tests."""
    import src.interfaces.api.routers.analysis as analysis_mod
    import src.interfaces.api.routers.map as map_mod
    from src.infrastructure.earth_engine_runtime.gee_authenticator import (
        GEEAuthenticator,
    )

    GEEAuthenticator._ee_initialized = False
    map_mod._gee_service = None
    analysis_mod._gee_service = None
    yield
    GEEAuthenticator._ee_initialized = False
    map_mod._gee_service = None
    analysis_mod._gee_service = None


@pytest.fixture
def gee_service():  # type: ignore[no-untyped-def]
    """Create a GEEService with fully mocked ee module."""
    mock_ee = _build_mocked_ee()

    patches = [patch(target, mock_ee) for target in _EE_PATCH_TARGETS]
    for p in patches:
        p.start()

    from src.infrastructure.earth_engine_runtime.gee_service import (
        GEEService,
    )

    service = GEEService()
    yield service

    for p in patches:
        p.stop()


@pytest.fixture
def api_client():  # type: ignore[no-untyped-def]
    """Create TestClient with fully mocked GEE backend."""
    mock_ee = _build_mocked_ee()

    patches = [patch(target, mock_ee) for target in _EE_PATCH_TARGETS]
    for p in patches:
        p.start()

    from src.interfaces.api.main import app

    client = TestClient(app)
    yield client

    for p in patches:
        p.stop()


# ── Unit Tests ──────────────────────────────────────────────


def test_gee_service_initialization_and_auth(gee_service) -> None:  # type: ignore[no-untyped-def]
    """GEEService initialises and reports healthy status."""
    health = gee_service.check_health()
    assert "status" in health
    assert "gee_initialized" in health


def test_roi_validation_valid_and_invalid(gee_service) -> None:  # type: ignore[no-untyped-def]
    """ROI bounding box and GeoJSON polygon validation."""
    bbox = [78.35, 17.30, 78.60, 17.50]
    assert gee_service.validate_roi(bbox) == bbox

    res_loc = gee_service.validate_roi(None, location_name="Hyderabad")
    assert len(res_loc) == 4

    geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [78.35, 17.3],
                [78.6, 17.3],
                [78.6, 17.5],
                [78.35, 17.5],
                [78.35, 17.3],
            ]
        ],
    }
    assert len(gee_service.validate_roi(geojson)) == 4

    with pytest.raises(InvalidROIError):
        gee_service.validate_roi([78.35, 17.30, 78.60])

    with pytest.raises(InvalidROIError):
        gee_service.validate_roi([200.0, 17.30, 78.60, 17.50])


def test_sentinel_rgb_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_sentinel_rgb returns an image and vis_params."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_sentinel_rgb(
        bounds=bounds,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["bands"] == ["B4", "B3", "B2"]


def test_sentinel_ndvi_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_ndvi_image computes normalizedDifference(B8, B4) inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_ndvi_image(
        bounds=bounds,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == -1.0
    assert vis_params["max"] == 1.0
    assert len(vis_params["palette"]) == 6


def test_sentinel_ndwi_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_ndwi_image computes normalizedDifference(B3, B8) inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_ndwi_image(
        bounds=bounds,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == -1.0
    assert vis_params["max"] == 1.0
    assert len(vis_params["palette"]) == 6


def test_sentinel_ndbi_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_ndbi_image computes normalizedDifference(B11, B8) inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_ndbi_image(
        bounds=bounds,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == -1.0
    assert vis_params["max"] == 1.0
    assert len(vis_params["palette"]) == 10


def test_landsat_lst_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_lst_image processes LANDSAT/LC08/C02/T1_L2 ST_B10 to Celsius inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_lst_image(
        bounds=bounds,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == 15.0
    assert vis_params["max"] == 50.0
    assert len(vis_params["palette"]) == 11


def test_ndbi_change_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_ndbi_change_image calculates NDBI_2025.subtract(NDBI_2016) inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_ndbi_change_image(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == -1.0
    assert vis_params["max"] == 1.0
    assert len(vis_params["palette"]) == 7


def test_lst_change_collection_query(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_lst_change_image calculates LST_2025.subtract(LST_2016) inside GEE."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    img, vis_params = gee_service.get_lst_change_image(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
    )
    assert img is not None
    assert vis_params["min"] == -10.0
    assert vis_params["max"] == 10.0
    assert len(vis_params["palette"]) == 7


def test_relationship_analysis_calculation(gee_service) -> None:  # type: ignore[no-untyped-def]
    """get_relationship_analysis performs 30m grid resampling and calculates Pearson r & OLS."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    res = gee_service.get_relationship_analysis(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
        sample_size=100,
        seed=42,
        location_name="Hyderabad",
    )
    assert res.location == "Hyderabad"
    assert res.analysis_resolution_m == 30
    assert res.sample_size == 100
    assert res.ndbi.native_resolution_m == 20
    assert res.lst.native_resolution_m == 30
    assert res.correlation.pearson_r == 1.0
    assert res.correlation.spearman_rho == 1.0
    assert res.regression.slope == 40.0
    assert res.regression.r_squared == 1.0
    assert len(res.scatter_points) == 100
    assert "Correlation does not establish causation." in res.interpretation
    assert "spatial autocorrelation" in res.autocorrelation_warning


def test_verify_spatial_means_not_used_for_correlation(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Verify correlation is computed from paired observations, NOT from spatial means."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    res = gee_service.get_relationship_analysis(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
        sample_size=100,
        seed=42,
        location_name="Hyderabad",
    )
    assert res.sample_size > 1
    assert res.correlation.pearson_r is not None
    assert not (res.ndbi.mean_change == res.correlation.pearson_r)


def test_get_utm_crs_metric_calculation() -> None:
    """Verify get_utm_crs produces valid projected metric UTM EPSG codes."""
    from src.infrastructure.earth_engine_runtime.gee_service import get_utm_crs

    # Hyderabad (78.47°E, 17.40°N) -> Zone 44N
    assert get_utm_crs([78.35, 17.30, 78.60, 17.50]) == "EPSG:32644"

    # Western Ghats (76.25°E, 11.25°N) -> Zone 43N
    assert get_utm_crs([75.00, 8.50, 77.50, 14.00]) == "EPSG:32643"

    # Southern Hemisphere (78.47°E, -17.40°S) -> Zone 44S
    assert get_utm_crs([78.35, -17.50, 78.60, -17.30]) == "EPSG:32744"


def test_relationship_analysis_metric_crs_metadata(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Verify get_relationship_analysis metadata includes metric projected CRS and 30m grid."""
    bounds = [78.35, 17.30, 78.60, 17.50]
    res = gee_service.get_relationship_analysis(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
        sample_size=100,
        seed=42,
        location_name="Hyderabad",
    )
    assert res.metadata.analysis_crs == "EPSG:32644"
    assert res.metadata.analysis_grid_m == 30
    assert res.analysis_resolution_m == 30
    assert res.metadata.analysis_crs != "EPSG:4326"  # Must NOT be EPSG:4326


def test_statistical_validation_consistency_identical_raw_sample(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Verify production API metrics match independent scipy.stats calculations."""
    import numpy as np
    import scipy.stats as stats

    bounds = [78.35, 17.30, 78.60, 17.50]
    res = gee_service.get_relationship_analysis(
        bounds=bounds,
        start_year=2016,
        end_year=2025,
        cloud_threshold=20.0,
        sample_size=100,
        seed=42,
        location_name="Hyderabad",
    )
    assert len(res.raw_sample) == 100
    raw_x = np.array([pt.delta_ndbi for pt in res.raw_sample], dtype=np.float64)
    raw_y = np.array([pt.delta_lst for pt in res.raw_sample], dtype=np.float64)

    ind_r = float(stats.pearsonr(raw_x, raw_y).statistic)
    ind_rho = float(stats.spearmanr(raw_x, raw_y).statistic)
    ind_reg = stats.linregress(raw_x, raw_y)

    assert round(ind_r, 4) == res.correlation.pearson_r
    assert round(ind_rho, 4) == res.correlation.spearman_rho
    assert round(float(ind_reg.slope), 4) == res.regression.slope
    assert round(float(ind_reg.intercept), 4) == res.regression.intercept
    assert round(float(ind_reg.rvalue**2), 4) == res.regression.r_squared




def test_tile_generation_and_caching(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Map tile generation and 10-minute cache hit behaviour."""
    req = TileRequest(
        lat=17.3850,
        lng=78.4867,
        zoom=10,
        start_date="2024-01-01",
        end_date="2024-12-31",
        cloud_threshold=20.0,
        location_name="Hyderabad",
        layer="sentinel_rgb",
    )

    resp1 = gee_service.get_map_tiles(req)
    assert resp1.success is True
    assert "{z}" in resp1.tile_url
    assert resp1.metadata.dataset == "COPERNICUS/S2_SR_HARMONIZED"

    resp2 = gee_service.get_map_tiles(req)
    assert resp2.mapid == resp1.mapid


def test_change_layers_tile_generation_and_metadata(gee_service) -> None:  # type: ignore[no-untyped-def]
    """ndbi_change and lst_change tile generation and metadata verification."""
    req_ndbi_change = TileRequest(
        location_name="Hyderabad",
        start_date="2016-01-01",
        end_date="2025-12-31",
        cloud_threshold=20.0,
        layer="ndbi_change",
    )
    req_lst_change = TileRequest(
        location_name="Hyderabad",
        start_date="2016-01-01",
        end_date="2025-12-31",
        cloud_threshold=20.0,
        layer="lst_change",
    )

    resp_ndbi = gee_service.get_map_tiles(req_ndbi_change)
    resp_lst = gee_service.get_map_tiles(req_lst_change)

    assert resp_ndbi.metadata.index == "ΔNDBI"
    assert resp_ndbi.metadata.formula == "NDBI_2025 - NDBI_2016"
    assert resp_ndbi.metadata.resolution_meters == 20

    assert resp_lst.metadata.index == "ΔLST"
    assert resp_lst.metadata.formula == "LST_2025 - LST_2016 (°C)"
    assert resp_lst.metadata.resolution_meters == 30


def test_invalid_layer_error_handling(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Unsupported layer returns InvalidROIError."""
    req_invalid = TileRequest(
        location_name="Hyderabad",
        layer="unsupported_layer",
    )
    with pytest.raises(InvalidROIError):
        gee_service.get_map_tiles(req_invalid)


def test_invalid_date_range_validation() -> None:  # type: ignore[no-untyped-def]
    """start_date >= end_date raises ValueError in TileRequest."""
    with pytest.raises(ValueError, match="must be earlier than end_date"):
        TileRequest(
            start_date="2025-12-31",
            end_date="2016-01-01",
        )

    with pytest.raises(ValueError, match="must be earlier than end_date"):
        TileRequest(
            start_date="2024-01-01",
            end_date="2024-01-01",
        )


def test_invalid_cloud_threshold_validation() -> None:  # type: ignore[no-untyped-def]
    """cloud_threshold < 0 or > 100 raises ValueError in TileRequest."""
    with pytest.raises(ValueError, match=r"cloud_threshold must be between 0\.0 and 100\.0"):
        TileRequest(cloud_threshold=-5.0)

    with pytest.raises(ValueError, match=r"cloud_threshold must be between 0\.0 and 100\.0"):
        TileRequest(cloud_threshold=150.0)


def test_all_five_layers_receive_same_research_parameters(gee_service) -> None:  # type: ignore[no-untyped-def]
    """All layers receive identical ROI, dates, and cloud threshold, reflected in metadata."""
    custom_start = "2016-01-01"
    custom_end = "2025-12-31"
    custom_cloud = 15.0
    custom_location = "Hyderabad"

    for lyr in ["sentinel_rgb", "ndvi", "ndwi", "ndbi", "lst", "ndbi_change", "lst_change"]:
        req = TileRequest(
            location_name=custom_location,
            start_date=custom_start,
            end_date=custom_end,
            cloud_threshold=custom_cloud,
            layer=lyr,
        )
        resp = gee_service.get_map_tiles(req)
        assert resp.success is True
        assert resp.metadata.cloud_threshold_pct == custom_cloud


def test_cache_sensitivity_to_date_roi_cloud_and_layer(gee_service) -> None:  # type: ignore[no-untyped-def]
    """Cache key isolates requests across date ranges, ROIs, cloud thresholds, and layers."""
    req_base = TileRequest(
        location_name="Hyderabad",
        start_date="2016-01-01",
        end_date="2025-12-31",
        cloud_threshold=20.0,
        layer="ndvi",
    )
    req_diff_dates = TileRequest(
        location_name="Hyderabad",
        start_date="2020-01-01",
        end_date="2025-12-31",
        cloud_threshold=20.0,
        layer="ndvi",
    )
    req_diff_roi = TileRequest(
        location_name="Assam",
        start_date="2016-01-01",
        end_date="2025-12-31",
        cloud_threshold=20.0,
        layer="ndvi",
    )
    req_diff_cloud = TileRequest(
        location_name="Hyderabad",
        start_date="2016-01-01",
        end_date="2025-12-31",
        cloud_threshold=10.0,
        layer="ndvi",
    )

    resp_base = gee_service.get_map_tiles(req_base)
    resp_dates = gee_service.get_map_tiles(req_diff_dates)
    resp_roi = gee_service.get_map_tiles(req_diff_roi)
    resp_cloud = gee_service.get_map_tiles(req_diff_cloud)

    assert resp_base.metadata.date_range != resp_dates.metadata.date_range
    assert resp_base.metadata.cloud_threshold_pct != resp_cloud.metadata.cloud_threshold_pct
    assert resp_base.metadata.image_id != resp_roi.metadata.image_id


# ── API Endpoint Tests ──────────────────────────────────────


def test_api_layers_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/map/layers returns active base layers and change analysis layers."""
    res = api_client.get("/api/v1/map/layers")
    assert res.status_code == 200
    layers = res.json()
    assert isinstance(layers, list)
    assert len(layers) >= 7
    assert layers[0]["id"] == "sentinel_rgb" and layers[0]["is_active"] is True
    assert layers[5]["id"] == "ndbi_change" and layers[5]["is_active"] is True
    assert layers[6]["id"] == "lst_change" and layers[6]["is_active"] is True


def test_api_tiles_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/map/tiles returns tile URL and metadata for requested layer."""
    res_rgb = api_client.get(
        "/api/v1/map/tiles",
        params={
            "location": "Hyderabad",
            "start_date": "2016-01-01",
            "end_date": "2025-12-31",
            "cloud": "15.0",
            "layer": "sentinel_rgb",
        },
    )
    assert res_rgb.status_code == 200
    assert res_rgb.json()["metadata"]["dataset"] == "COPERNICUS/S2_SR_HARMONIZED"

    res_ndbi_change = api_client.get(
        "/api/v1/map/tiles",
        params={
            "location": "Hyderabad",
            "start_date": "2016-01-01",
            "end_date": "2025-12-31",
            "cloud": "15.0",
            "layer": "ndbi_change",
        },
    )
    assert res_ndbi_change.status_code == 200
    data_change = res_ndbi_change.json()
    assert data_change["metadata"]["index"] == "ΔNDBI"
    assert data_change["metadata"]["formula"] == "NDBI_2025 - NDBI_2016"


def test_api_analysis_change_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/analysis/change returns ΔNDBI and ΔLST change analysis response."""
    res = api_client.get(
        "/api/v1/analysis/change",
        params={
            "location": "Hyderabad",
            "start_year": 2016,
            "end_year": 2025,
            "cloud": 20.0,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Hyderabad"
    assert data["baseline_year"] == 2016
    assert data["end_year"] == 2025
    assert "ndbi_change" in data["layers"]
    assert "lst_change" in data["layers"]
    assert data["layers"]["ndbi_change"]["metadata"]["index"] == "ΔNDBI"
    assert data["layers"]["lst_change"]["metadata"]["index"] == "ΔLST"


def test_api_analysis_relationship_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/analysis/relationship returns spatial relationship metrics."""
    res = api_client.get(
        "/api/v1/analysis/relationship",
        params={
            "location": "Hyderabad",
            "start_year": 2016,
            "end_year": 2025,
            "cloud": 20.0,
            "sample_size": 100,
            "seed": 42,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Hyderabad"
    assert data["analysis_resolution_m"] == 30
    assert data["sample_size"] == 100
    assert data["correlation"]["pearson_r"] == 1.0
    assert data["correlation"]["spearman_rho"] == 1.0
    assert data["regression"]["slope"] == 40.0
    assert len(data["scatter_points"]) == 100


def test_api_analysis_relationship_invalid_params(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/analysis/relationship returns HTTP 400 Bad Request on invalid inputs."""
    res_year = api_client.get(
        "/api/v1/analysis/relationship",
        params={"start_year": 2025, "end_year": 2016},
    )
    assert res_year.status_code == 400
    assert "must be earlier than end_year" in res_year.json()["detail"]

    res_cloud = api_client.get(
        "/api/v1/analysis/relationship",
        params={"cloud": 150.0},
    )
    assert res_cloud.status_code == 400
    assert "cloud_threshold must be between" in res_cloud.json()["detail"]


def test_api_analysis_change_invalid_years(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/analysis/change with start_year >= end_year returns HTTP 400 Bad Request."""
    res_invalid = api_client.get(
        "/api/v1/analysis/change",
        params={
            "location": "Hyderabad",
            "start_year": 2025,
            "end_year": 2016,
        },
    )
    assert res_invalid.status_code == 400
    assert "must be earlier than end_year" in res_invalid.json()["detail"]


def test_api_invalid_parameter_returns_400(api_client) -> None:  # type: ignore[no-untyped-def]
    """Invalid date range or cloud threshold returns HTTP 400 Bad Request."""
    res_invalid_date = api_client.get(
        "/api/v1/map/tiles",
        params={"start_date": "2025-12-31", "end_date": "2016-01-01"},
    )
    assert res_invalid_date.status_code == 400
    assert "must be earlier than end_date" in res_invalid_date.json()["detail"]

    res_invalid_cloud = api_client.get(
        "/api/v1/map/tiles",
        params={"cloud": "-10.0"},
    )
    assert res_invalid_cloud.status_code == 400
    assert "cloud_threshold must be between 0.0 and 100.0" in res_invalid_cloud.json()["detail"]


def test_api_metadata_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/map/metadata returns layer metadata."""
    res_lst = api_client.get(
        "/api/v1/map/metadata",
        params={
            "location": "Hyderabad",
            "start_date": "2016-01-01",
            "end_date": "2025-12-31",
            "cloud": "20.0",
            "layer": "lst",
        },
    )
    assert res_lst.status_code == 200
    meta = res_lst.json()
    assert meta["dataset"] == "LANDSAT/LC08/C02/T1_L2"
    assert meta["index"] == "LST"
    assert meta["bands"] == ["ST_B10"]
    assert meta["resolution_meters"] == 30
    assert meta["date_range"] == "2016-01-01 to 2025-12-31"


def test_api_health_endpoint(api_client) -> None:  # type: ignore[no-untyped-def]
    """GET /api/v1/map/health returns status."""
    res = api_client.get("/api/v1/map/health")
    assert res.status_code == 200
    health = res.json()
    assert "status" in health
