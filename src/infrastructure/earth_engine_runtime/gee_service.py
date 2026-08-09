"""GEE service: Sentinel-2 RGB/NDVI/NDWI/NDBI/LST, ΔNDBI/ΔLST change, and spatial relationship."""

import hashlib
import math
import random
import time
from typing import Any, ClassVar

import ee
import numpy as np
import scipy.stats as stats  # type: ignore[import-untyped]

from src.infrastructure.earth_engine_runtime.exceptions import (
    InvalidROIError,
    TileGenerationError,
)
from src.infrastructure.earth_engine_runtime.gee_authenticator import (
    GEEAuthenticator,
)
from src.infrastructure.earth_engine_runtime.tile_service import TileService
from src.infrastructure.earth_engine_runtime.types import (
    CorrelationMetrics,
    LayerInfo,
    MapMetadata,
    RegressionMetrics,
    RelationshipAnalysisResponse,
    RelationshipMetadata,
    ScatterPoint,
    TileRequest,
    TileResponse,
    VariableStats,
)
from src.shared.config.settings import get_settings
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

# Known geographic location bounding boxes [min_lon, min_lat, max_lon, max_lat]
LOCATION_BOUNDS: dict[str, list[float]] = {
    "hyderabad": [78.35, 17.30, 78.60, 17.50],
    "assam": [90.50, 25.80, 95.00, 27.50],
    "western ghats": [75.00, 8.50, 77.50, 14.00],
    "amazon": [-70.00, -10.00, -55.00, 2.00],
}

# Standard NDVI color palette: brown -> light yellow -> teal -> dark teal green
NDVI_PALETTE: list[str] = [
    "8c510a",
    "d8b365",
    "f6e8c3",
    "c7eae5",
    "5ab4ac",
    "01665e",
]

# Standard NDWI color palette: brown/tan for dry land -> cyan -> deep blue
NDWI_PALETTE: list[str] = [
    "8c510a",
    "d8b365",
    "f6e8c3",
    "c7eae5",
    "3388ff",
    "000080",
]

# Built-up NDBI color palette: blue/cyan (water/veg) -> yellow (soil) -> orange/red (urban)
NDBI_PALETTE: list[str] = [
    "313695",
    "74add1",
    "abd9e9",
    "e0f3f8",
    "ffffbf",
    "fee090",
    "fdae61",
    "f46d43",
    "d73027",
    "a50026",
]

# Thermal LST color palette: cool blue -> light cyan -> soft yellow -> orange -> dark red
LST_PALETTE: list[str] = [
    "313695",
    "4575b4",
    "74add1",
    "abd9e9",
    "e0f3f8",
    "ffffbf",
    "fee090",
    "fdae61",
    "f46d43",
    "d73027",
    "a50026",
]

# Diverging spatial change palette: blue (decrease) -> white (no change) -> red (increase)
CHANGE_PALETTE: list[str] = [
    "2166ac",
    "67a9cf",
    "d1e5f0",
    "f7f7f7",
    "fddbc7",
    "ef8a62",
    "b2182b",
]


def get_utm_crs(bounds: list[float]) -> str:
    """Calculate UTM projected metric CRS for bounding box [min_lon, min_lat, max_lon, max_lat]."""
    center_lon = (bounds[0] + bounds[2]) / 2.0
    center_lat = (bounds[1] + bounds[3]) / 2.0
    zone_number = math.floor((center_lon + 180.0) / 6.0) + 1
    if center_lat >= 0:
        return f"EPSG:{32600 + zone_number}"
    return f"EPSG:{32700 + zone_number}"


class GEEService:
    """Production service for Earth Engine imagery, Leaflet tiles, and spatial analysis."""

    _tile_cache: ClassVar[dict[str, tuple[TileResponse, float]]] = {}
    _relationship_cache: ClassVar[dict[str, tuple[RelationshipAnalysisResponse, float]]] = {}

    def __init__(self) -> None:
        self.authenticator = GEEAuthenticator()
        self.authenticator.authenticate()
        self.settings = get_settings()

    def validate_roi(  # noqa: C901
        self,
        roi: dict[str, Any] | list[float] | None = None,
        location_name: str | None = None,
    ) -> list[float]:
        """Validate and resolve region of interest (ROI) to bounding box.

        Returns:
            [min_lon, min_lat, max_lon, max_lat]
        """
        if roi is not None:
            if isinstance(roi, list):
                if len(roi) != 4:
                    raise InvalidROIError(
                        f"Bounding box list must contain 4 elements, got {len(roi)}: {roi}"
                    )
                min_lon, min_lat, max_lon, max_lat = roi
                if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
                    raise InvalidROIError(f"Invalid longitude range in ROI: {roi}")
                if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
                    raise InvalidROIError(f"Invalid latitude range in ROI: {roi}")
                if min_lon >= max_lon or min_lat >= max_lat:
                    raise InvalidROIError(f"Inverted bounding box in ROI: {roi}")
                return [float(min_lon), float(min_lat), float(max_lon), float(max_lat)]

            if isinstance(roi, dict) and roi.get("type") == "Polygon":
                coords = roi.get("coordinates", [[]])[0]
                if not coords or len(coords) < 3:
                    raise InvalidROIError("Polygon GeoJSON coordinates list is empty or invalid.")
                lons = [pt[0] for pt in coords]
                lats = [pt[1] for pt in coords]
                return [
                    float(min(lons)),
                    float(min(lats)),
                    float(max(lons)),
                    float(max(lats)),
                ]

        if location_name:
            matched_key = location_name.lower().strip()
            for key, bbox in LOCATION_BOUNDS.items():
                if key in matched_key:
                    return list(bbox)

        # Default fallback to Hyderabad ROI
        return list(LOCATION_BOUNDS["hyderabad"])

    # ── Sentinel-2 RGB composite ────────────────────────────

    def get_sentinel_rgb(
        self,
        bounds: list[float],
        start_date: str,
        end_date: str,
        cloud_threshold: float,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Query COPERNICUS/S2_SR_HARMONIZED for RGB median composite."""
        vis_params: dict[str, Any] = {
            "bands": ["B4", "B3", "B2"],
            "min": 0.0,
            "max": 3000.0,
        }

        try:
            min_lon, min_lat, max_lon, max_lat = bounds
            geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(
                    ee.Filter.lte(
                        "CLOUDY_PIXEL_PERCENTAGE",
                        cloud_threshold,
                    )
                )
            )

            composite = collection.select(["B4", "B3", "B2"]).median().clip(geometry)

            logger.info(
                "Sentinel-2 RGB composite built",
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold,
            )
            return composite, vis_params

        except Exception as exc:
            logger.error("Sentinel-2 RGB query FAILED", error=str(exc))
            raise TileGenerationError(f"Sentinel-2 RGB query failed: {exc}") from exc

    # ── Sentinel-2 NDVI raster ──────────────────────────────

    def get_ndvi_image(
        self,
        bounds: list[float],
        start_date: str,
        end_date: str,
        cloud_threshold: float,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Query COPERNICUS/S2_SR_HARMONIZED and compute NDVI = (B8 - B4) / (B8 + B4)."""
        vis_params: dict[str, Any] = {
            "min": -1.0,
            "max": 1.0,
            "palette": NDVI_PALETTE,
        }

        try:
            min_lon, min_lat, max_lon, max_lat = bounds
            geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(
                    ee.Filter.lte(
                        "CLOUDY_PIXEL_PERCENTAGE",
                        cloud_threshold,
                    )
                )
            )

            s2_median = collection.select(["B8", "B4"]).median()
            ndvi_composite = s2_median.normalizedDifference(["B8", "B4"]).clip(geometry)

            logger.info(
                "Sentinel-2 NDVI composite calculated inside GEE",
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold,
            )
            return ndvi_composite, vis_params

        except Exception as exc:
            logger.error("Sentinel-2 NDVI query FAILED", error=str(exc))
            raise TileGenerationError(f"Sentinel-2 NDVI query failed: {exc}") from exc

    # ── Sentinel-2 NDWI raster ──────────────────────────────

    def get_ndwi_image(
        self,
        bounds: list[float],
        start_date: str,
        end_date: str,
        cloud_threshold: float,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Query COPERNICUS/S2_SR_HARMONIZED and compute NDWI = (B3 - B8) / (B3 + B8)."""
        vis_params: dict[str, Any] = {
            "min": -1.0,
            "max": 1.0,
            "palette": NDWI_PALETTE,
        }

        try:
            min_lon, min_lat, max_lon, max_lat = bounds
            geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(
                    ee.Filter.lte(
                        "CLOUDY_PIXEL_PERCENTAGE",
                        cloud_threshold,
                    )
                )
            )

            s2_median = collection.select(["B3", "B8"]).median()
            ndwi_composite = s2_median.normalizedDifference(["B3", "B8"]).clip(geometry)

            logger.info(
                "Sentinel-2 NDWI composite calculated inside GEE",
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold,
            )
            return ndwi_composite, vis_params

        except Exception as exc:
            logger.error("Sentinel-2 NDWI query FAILED", error=str(exc))
            raise TileGenerationError(f"Sentinel-2 NDWI query failed: {exc}") from exc

    # ── Sentinel-2 NDBI raster ──────────────────────────────

    def get_ndbi_image(
        self,
        bounds: list[float],
        start_date: str,
        end_date: str,
        cloud_threshold: float,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Query COPERNICUS/S2_SR_HARMONIZED and compute NDBI = (B11 - B8) / (B11 + B8)."""
        vis_params: dict[str, Any] = {
            "min": -1.0,
            "max": 1.0,
            "palette": NDBI_PALETTE,
        }

        try:
            min_lon, min_lat, max_lon, max_lat = bounds
            geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(
                    ee.Filter.lte(
                        "CLOUDY_PIXEL_PERCENTAGE",
                        cloud_threshold,
                    )
                )
            )

            s2_median = collection.select(["B11", "B8"]).median()
            ndbi_composite = s2_median.normalizedDifference(["B11", "B8"]).clip(geometry)

            logger.info(
                "Sentinel-2 NDBI composite calculated inside GEE",
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold,
            )
            return ndbi_composite, vis_params

        except Exception as exc:
            logger.error("Sentinel-2 NDBI query FAILED", error=str(exc))
            raise TileGenerationError(f"Sentinel-2 NDBI query failed: {exc}") from exc

    # ── Landsat 8/9 LST raster ──────────────────────────────

    def get_lst_image(
        self,
        bounds: list[float],
        start_date: str,
        end_date: str,
        cloud_threshold: float,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Query LANDSAT/LC08/C02/T1_L2 (+ LC09) and compute LST (°C)."""
        vis_params: dict[str, Any] = {
            "min": 15.0,
            "max": 50.0,
            "palette": LST_PALETTE,
        }

        try:
            min_lon, min_lat, max_lon, max_lat = bounds
            geometry = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

            l8_coll = (
                ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                .filterBounds(geometry)
                .filterDate(start_date, end_date)
                .filter(ee.Filter.lte("CLOUD_COVER", cloud_threshold))
            )

            coll = l8_coll
            try:
                l9_coll = (
                    ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
                    .filterBounds(geometry)
                    .filterDate(start_date, end_date)
                    .filter(ee.Filter.lte("CLOUD_COVER", cloud_threshold))
                )
                coll = l8_coll.merge(l9_coll)
            except Exception as e:
                logger.debug("Landsat 9 merge skipped", reason=str(e))

            def process_landsat_st(img: ee.Image) -> ee.Image:
                qa = img.select("QA_PIXEL")
                mask = (
                    qa.bitwiseAnd(1 << 0)
                    .eq(0)
                    .And(qa.bitwiseAnd(1 << 1).eq(0))
                    .And(qa.bitwiseAnd(1 << 3).eq(0))
                    .And(qa.bitwiseAnd(1 << 4).eq(0))
                    .And(qa.bitwiseAnd(1 << 5).eq(0))
                )
                st_b10 = img.select("ST_B10")
                celsius = st_b10.multiply(0.00341802).add(149.0).subtract(273.15)
                return celsius.updateMask(mask)  # type: ignore[no-any-return]

            processed = coll.map(process_landsat_st)
            lst_median = processed.median().clip(geometry)

            logger.info(
                "Landsat LST composite calculated inside GEE",
                start_date=start_date,
                end_date=end_date,
                cloud_threshold=cloud_threshold,
            )
            return lst_median, vis_params

        except Exception as exc:
            logger.error("Landsat LST query FAILED", error=str(exc))
            raise TileGenerationError(f"Landsat LST query failed: {exc}") from exc

    # ── NDBI Spatial Change (2016 vs 2025) ──────────────────

    def get_ndbi_change_image(
        self,
        bounds: list[float],
        start_year: int = 2016,
        end_year: int = 2025,
        cloud_threshold: float = 20.0,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Compute delta NDBI = NDBI(end_year) - NDBI(start_year) inside GEE."""
        vis_params: dict[str, Any] = {
            "min": -1.0,
            "max": 1.0,
            "palette": CHANGE_PALETTE,
        }

        try:
            ndbi_baseline, _ = self.get_ndbi_image(
                bounds=bounds,
                start_date=f"{start_year}-01-01",
                end_date=f"{start_year}-12-31",
                cloud_threshold=cloud_threshold,
            )
            ndbi_endpoint, _ = self.get_ndbi_image(
                bounds=bounds,
                start_date=f"{end_year}-01-01",
                end_date=f"{end_year}-12-31",
                cloud_threshold=cloud_threshold,
            )

            delta_ndbi = ndbi_endpoint.subtract(ndbi_baseline)

            logger.info(
                "Sentinel-2 ΔNDBI change calculated inside GEE",
                start_year=start_year,
                end_year=end_year,
                cloud_threshold=cloud_threshold,
            )
            return delta_ndbi, vis_params

        except Exception as exc:
            logger.error("Sentinel-2 ΔNDBI change calculation FAILED", error=str(exc))
            raise TileGenerationError(f"Sentinel-2 ΔNDBI change query failed: {exc}") from exc

    # ── LST Spatial Change (2016 vs 2025) ───────────────────

    def get_lst_change_image(
        self,
        bounds: list[float],
        start_year: int = 2016,
        end_year: int = 2025,
        cloud_threshold: float = 20.0,
    ) -> tuple[ee.Image, dict[str, Any]]:
        """Compute delta LST = LST(end_year) - LST(start_year) (°C) inside GEE."""
        vis_params: dict[str, Any] = {
            "min": -10.0,
            "max": 10.0,
            "palette": CHANGE_PALETTE,
        }

        try:
            lst_baseline, _ = self.get_lst_image(
                bounds=bounds,
                start_date=f"{start_year}-01-01",
                end_date=f"{start_year}-12-31",
                cloud_threshold=cloud_threshold,
            )
            lst_endpoint, _ = self.get_lst_image(
                bounds=bounds,
                start_date=f"{end_year}-01-01",
                end_date=f"{end_year}-12-31",
                cloud_threshold=cloud_threshold,
            )

            delta_lst = lst_endpoint.subtract(lst_baseline)

            logger.info(
                "Landsat ΔLST change calculated inside GEE",
                start_year=start_year,
                end_year=end_year,
                cloud_threshold=cloud_threshold,
            )
            return delta_lst, vis_params

        except Exception as exc:
            logger.error("Landsat ΔLST change calculation FAILED", error=str(exc))
            raise TileGenerationError(f"Landsat ΔLST change query failed: {exc}") from exc

    # ── ΔNDBI ↔ ΔLST Spatial Relationship Analysis ─────────

    def get_relationship_analysis(  # noqa: C901
        self,
        bounds: list[float],
        start_year: int = 2016,
        end_year: int = 2025,
        cloud_threshold: float = 20.0,
        sample_size: int = 5000,
        seed: int = 42,
        location_name: str = "Hyderabad",
    ) -> RelationshipAnalysisResponse:
        """Perform spatial relationship analysis between ΔNDBI and ΔLST on metric 30m grid."""
        actual_num_pixels = min(max(sample_size, 100), 5000)
        utm_crs = get_utm_crs(bounds)

        cache_key_str = (
            f"rel_{location_name}_{bounds}_{start_year}_{end_year}_"
            f"{cloud_threshold}_{actual_num_pixels}_{seed}_{utm_crs}"
        )
        cache_key = hashlib.sha256(cache_key_str.encode("utf-8")).hexdigest()

        now = time.time()
        ttl_sec = self.settings.GEE_CACHE_TTL_SEC

        if cache_key in self._relationship_cache:
            cached_res, ts = self._relationship_cache[cache_key]
            if now - ts < ttl_sec:
                logger.info("GEE relationship cache HIT", cache_key=cache_key[:10])
                return cached_res

        t0 = time.time()

        # 1. Compute baseline and endpoint rasters inside GEE
        delta_ndbi, _ = self.get_ndbi_change_image(bounds, start_year, end_year, cloud_threshold)
        delta_lst, _ = self.get_lst_change_image(bounds, start_year, end_year, cloud_threshold)

        # 2. Combine rasters into 2-band image and valid pixel mask
        combined_img = ee.Image(
            [delta_ndbi.rename("delta_ndbi"), delta_lst.rename("delta_lst")]
        )
        valid_mask = delta_ndbi.mask().And(delta_lst.mask())
        masked_combined = combined_img.updateMask(valid_mask)

        # 3. GEE Spatial Sampling: Evaluate on metric 30m UTM grid directly inside sample()
        geometry = ee.Geometry.Rectangle(bounds)

        try:
            samples = masked_combined.sample(
                region=geometry,
                scale=30,
                projection=utm_crs,
                numPixels=actual_num_pixels,
                seed=seed,
                geometries=False,
            )
            sample_info = samples.getInfo()
            features = sample_info.get("features", []) if isinstance(sample_info, dict) else []
        except Exception as exc:
            logger.error("GEE spatial sampling FAILED", error=str(exc))
            raise TileGenerationError(f"GEE spatial sampling failed: {exc}") from exc

        # 4. Extract paired numeric arrays in Python (retaining full precision)
        x_list: list[float] = []
        y_list: list[float] = []

        for feat in features:
            props = feat.get("properties", {})
            val_ndbi = props.get("delta_ndbi")
            val_lst = props.get("delta_lst")
            if val_ndbi is not None and val_lst is not None:
                try:
                    f_ndbi = float(val_ndbi)
                    f_lst = float(val_lst)
                    if not (
                        math.isnan(f_ndbi)
                        or math.isnan(f_lst)
                        or math.isinf(f_ndbi)
                        or math.isinf(f_lst)
                    ):
                        x_list.append(f_ndbi)
                        y_list.append(f_lst)
                except (ValueError, TypeError):
                    continue

        n_obs = len(x_list)
        if n_obs < 3:
            raise TileGenerationError(
                f"Insufficient paired observations ({n_obs}) for spatial relationship analysis."
            )

        x_arr = np.array(x_list, dtype=np.float64)
        y_arr = np.array(y_list, dtype=np.float64)

        # 5. Statistical Calculations from Paired Observations
        mean_x = float(np.mean(x_arr))
        std_x = float(np.std(x_arr, ddof=1)) if n_obs > 1 else 0.0

        mean_y = float(np.mean(y_arr))
        std_y = float(np.std(y_arr, ddof=1)) if n_obs > 1 else 0.0

        # Handle zero-variance gracefully
        if std_x == 0.0 or std_y == 0.0:
            pearson_r = 0.0
            pearson_p: float | None = 1.0
            spearman_rho = 0.0
            spearman_p: float | None = 1.0
            slope = 0.0
            intercept = mean_y
            r_squared = 0.0
        else:
            p_res = stats.pearsonr(x_arr, y_arr)
            pearson_r = float(p_res.statistic)
            pearson_p = float(p_res.pvalue) if not math.isnan(p_res.pvalue) else None

            s_res = stats.spearmanr(x_arr, y_arr)
            spearman_rho = float(s_res.statistic)
            spearman_p = float(s_res.pvalue) if not math.isnan(s_res.pvalue) else None

            reg_res = stats.linregress(x_arr, y_arr)
            slope = float(reg_res.slope)
            intercept = float(reg_res.intercept)
            r_squared = float(reg_res.rvalue**2)

        # 6. Visualization Sample (Deterministically max 2,000 scatter points)
        rng = random.Random(seed)
        all_indices = list(range(n_obs))
        if n_obs > 2000:
            viz_indices = rng.sample(all_indices, 2000)
        else:
            viz_indices = all_indices

        scatter_points = [
            ScatterPoint(
                delta_ndbi=round(float(x_arr[i]), 5),
                delta_lst=round(float(y_arr[i]), 3),
            )
            for i in viz_indices
        ]

        # 7. Non-causal Interpretation
        if pearson_r > 0.05:
            interp = (
                "Positive spatial association: locations with larger increases in NDBI "
                "tend to show larger increases in LST."
            )
        elif pearson_r < -0.05:
            interp = (
                "Negative spatial association: locations with larger increases in NDBI "
                "tend to show lower changes in LST."
            )
        else:
            interp = "Little linear spatial association was detected between ΔNDBI and ΔLST."

        interp += " Correlation does not establish causation."

        warning = (
            "Pixel-level observations may exhibit spatial autocorrelation; correlation and "
            "p-values should therefore be interpreted as exploratory spatial associations "
            "rather than independent-sample inference."
        )

        raw_sample = [
            ScatterPoint(
                delta_ndbi=float(x_arr[i]),
                delta_lst=float(y_arr[i]),
            )
            for i in range(n_obs)
        ]

        response = RelationshipAnalysisResponse(
            location=location_name,
            baseline_year=start_year,
            end_year=end_year,
            cloud_threshold=cloud_threshold,
            analysis_resolution_m=30,
            sample_size=n_obs,
            ndbi=VariableStats(
                native_resolution_m=20,
                mean_change=round(mean_x, 5),
                std_change=round(std_x, 5),
            ),
            lst=VariableStats(
                native_resolution_m=30,
                mean_change=round(mean_y, 3),
                std_change=round(std_y, 3),
            ),
            correlation=CorrelationMetrics(
                pearson_r=round(pearson_r, 4),
                pearson_p_value=pearson_p,
                spearman_rho=round(spearman_rho, 4),
                spearman_p_value=spearman_p,
            ),
            regression=RegressionMetrics(
                slope=round(slope, 4),
                intercept=round(intercept, 4),
                r_squared=round(r_squared, 4),
            ),
            scatter_points=scatter_points,
            raw_sample=raw_sample,
            metadata=RelationshipMetadata(
                baseline_year=start_year,
                end_year=end_year,
                ndbi_dataset="COPERNICUS/S2_SR_HARMONIZED",
                ndbi_native_resolution_m=20,
                lst_dataset="LANDSAT/LC08/C02/T1_L2",
                lst_native_resolution_m=30,
                analysis_crs=utm_crs,
                analysis_grid_m=30,
                ndbi_resampling="bilinear",
                sampling_method="controlled random spatial sample",
                seed=seed,
                cloud_threshold_pct=cloud_threshold,
                roi=bounds,
            ),
            interpretation=interp,
            autocorrelation_warning=warning,
        )

        self._relationship_cache[cache_key] = (response, now)
        elapsed = time.time() - t0
        logger.info(
            "Completed GEE spatial relationship analysis",
            location=location_name,
            sample_size=n_obs,
            pearson_r=round(pearson_r, 4),
            r_squared=round(r_squared, 4),
            elapsed_sec=round(elapsed, 3),
            crs=utm_crs,
        )
        return response

    # ── Tile generation with cache ──────────────────────────

    def get_map_tiles(self, req: TileRequest) -> TileResponse:  # noqa: C901
        """Generate Leaflet tiles for requested layer; uses 10-min TTL cache."""
        layer = (req.layer or "sentinel_rgb").lower()

        valid_layers = (
            "sentinel_rgb",
            "ndvi",
            "ndwi",
            "ndbi",
            "lst",
            "ndbi_change",
            "lst_change",
        )
        if layer not in valid_layers:
            raise InvalidROIError(
                f"Unsupported layer '{req.layer}'. "
                "Valid: sentinel_rgb, ndvi, ndwi, ndbi, lst, ndbi_change, lst_change."
            )

        bounds = self.validate_roi(req.roi, req.location_name)

        try:
            start_year = int(req.start_date[:4])
            end_year = int(req.end_date[:4])
        except (ValueError, IndexError, TypeError):
            start_year, end_year = 2016, 2025

        cache_key_str = f"{layer}_{bounds}_{req.start_date}_{req.end_date}_{req.cloud_threshold}"
        cache_key = hashlib.sha256(cache_key_str.encode("utf-8")).hexdigest()

        now = time.time()
        ttl_sec = self.settings.GEE_CACHE_TTL_SEC

        if cache_key in self._tile_cache:
            cached, ts = self._tile_cache[cache_key]
            if now - ts < ttl_sec:
                logger.info(
                    "GEE tile cache HIT",
                    layer=layer,
                    cache_key=cache_key[:10],
                )
                return cached

        t0 = time.time()

        if layer == "ndvi":
            image, vis_params = self.get_ndvi_image(
                bounds=bounds,
                start_date=req.start_date,
                end_date=req.end_date,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Sentinel-2 NDVI"
            metadata = MapMetadata(
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                collection_name="Sentinel-2 Surface Reflectance (Harmonized)",
                date_range=f"{req.start_date} to {req.end_date}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["B8", "B4"],
                resolution_meters=10,
                projection="EPSG:4326",
                image_id=f"S2_NDVI_{start_year}_{cache_key[:8]}",
                index="NDVI",
                formula="(B8 - B4) / (B8 + B4)",
                palette=NDVI_PALETTE,
                vis_min=-1.0,
                vis_max=1.0,
            )
        elif layer == "ndwi":
            image, vis_params = self.get_ndwi_image(
                bounds=bounds,
                start_date=req.start_date,
                end_date=req.end_date,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Sentinel-2 NDWI"
            metadata = MapMetadata(
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                collection_name="Sentinel-2 Surface Reflectance (Harmonized)",
                date_range=f"{req.start_date} to {req.end_date}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["B3", "B8"],
                resolution_meters=10,
                projection="EPSG:4326",
                image_id=f"S2_NDWI_{start_year}_{cache_key[:8]}",
                index="NDWI",
                formula="(B3 - B8) / (B3 + B8)",
                palette=NDWI_PALETTE,
                vis_min=-1.0,
                vis_max=1.0,
            )
        elif layer == "ndbi":
            image, vis_params = self.get_ndbi_image(
                bounds=bounds,
                start_date=req.start_date,
                end_date=req.end_date,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Sentinel-2 NDBI"
            metadata = MapMetadata(
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                collection_name="Sentinel-2 Surface Reflectance (Harmonized)",
                date_range=f"{req.start_date} to {req.end_date}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["B11", "B8"],
                resolution_meters=20,
                projection="EPSG:4326",
                image_id=f"S2_NDBI_{start_year}_{cache_key[:8]}",
                index="NDBI",
                formula="(B11 - B8) / (B11 + B8)",
                palette=NDBI_PALETTE,
                vis_min=-1.0,
                vis_max=1.0,
            )
        elif layer == "lst":
            image, vis_params = self.get_lst_image(
                bounds=bounds,
                start_date=req.start_date,
                end_date=req.end_date,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Landsat-8/9 LST"
            metadata = MapMetadata(
                dataset="LANDSAT/LC08/C02/T1_L2",
                collection_name="Landsat 8/9 Collection 2 Level-2 Surface Temperature",
                date_range=f"{req.start_date} to {req.end_date}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["ST_B10"],
                resolution_meters=30,
                projection="EPSG:4326",
                image_id=f"L89_LST_{start_year}_{cache_key[:8]}",
                index="LST",
                formula="ST_B10 * 0.00341802 + 149.0 - 273.15 (°C)",
                palette=LST_PALETTE,
                vis_min=15.0,
                vis_max=50.0,
            )
        elif layer == "ndbi_change":
            image, vis_params = self.get_ndbi_change_image(
                bounds=bounds,
                start_year=start_year,
                end_year=end_year,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Sentinel-2 NDBI Change"
            metadata = MapMetadata(
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                collection_name="Sentinel-2 Surface Reflectance (Harmonized)",
                date_range=f"{start_year} to {end_year}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["B11", "B8"],
                resolution_meters=20,
                projection="EPSG:4326",
                image_id=f"S2_NDBI_CHANGE_{start_year}_{end_year}_{cache_key[:8]}",
                index="ΔNDBI",
                formula=f"NDBI_{end_year} - NDBI_{start_year}",
                palette=CHANGE_PALETTE,
                vis_min=-1.0,
                vis_max=1.0,
            )
        elif layer == "lst_change":
            image, vis_params = self.get_lst_change_image(
                bounds=bounds,
                start_year=start_year,
                end_year=end_year,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Landsat LST Change"
            metadata = MapMetadata(
                dataset="LANDSAT/LC08/C02/T1_L2",
                collection_name="Landsat 8/9 Collection 2 Level-2 Surface Temperature",
                date_range=f"{start_year} to {end_year}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["ST_B10"],
                resolution_meters=30,
                projection="EPSG:4326",
                image_id=f"L89_LST_CHANGE_{start_year}_{end_year}_{cache_key[:8]}",
                index="ΔLST",
                formula=f"LST_{end_year} - LST_{start_year} (°C)",
                palette=CHANGE_PALETTE,
                vis_min=-10.0,
                vis_max=10.0,
            )
        else:
            image, vis_params = self.get_sentinel_rgb(
                bounds=bounds,
                start_date=req.start_date,
                end_date=req.end_date,
                cloud_threshold=req.cloud_threshold,
            )
            layer_label = "Sentinel-2 RGB"
            metadata = MapMetadata(
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                collection_name="Sentinel-2 Surface Reflectance (Harmonized)",
                date_range=f"{req.start_date} to {req.end_date}",
                cloud_threshold_pct=req.cloud_threshold,
                bands=["B4", "B3", "B2"],
                resolution_meters=10,
                projection="EPSG:4326",
                image_id=f"S2_RGB_{start_year}_{cache_key[:8]}",
                index="RGB",
                formula="Bands B4 (Red), B3 (Green), B2 (Blue)",
                palette=None,
                vis_min=0.0,
                vis_max=3000.0,
            )

        tile_data = TileService.generate_tile(
            image=image,
            vis_params=vis_params,
            layer_name=layer_label,
        )

        response = TileResponse(
            success=True,
            mapid=tile_data["mapid"],
            token=tile_data["token"],
            tile_url=tile_data["tile_url"],
            metadata=metadata,
        )

        self._tile_cache[cache_key] = (response, now)
        elapsed = time.time() - t0
        logger.info(
            "Generated GEE map tiles",
            layer=layer,
            elapsed_sec=round(elapsed, 3),
            mapid=tile_data["mapid"][:16],
        )
        return response

    # ── Layers / Metadata / Health ──────────────────────────

    def get_layers(self) -> list[LayerInfo]:
        """Available map layers."""
        return [
            LayerInfo(
                id="sentinel_rgb",
                name="Sentinel-2 True Color (RGB)",
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                is_active=True,
                description="10 m true-color surface reflectance.",
            ),
            LayerInfo(
                id="ndvi",
                name="Normalized Difference Vegetation Index (NDVI)",
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                is_active=True,
                description="10 m vegetation vigor index calculated via (B8 - B4)/(B8 + B4).",
            ),
            LayerInfo(
                id="ndwi",
                name="Normalized Difference Water Index (NDWI)",
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                is_active=True,
                description="10 m water index calculated via (B3 - B8)/(B3 + B8).",
            ),
            LayerInfo(
                id="ndbi",
                name="Normalized Difference Built-up Index (NDBI)",
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                is_active=True,
                description="20 m built-up index calculated via (B11 - B8)/(B11 + B8).",
            ),
            LayerInfo(
                id="lst",
                name="Land Surface Temperature (LST)",
                dataset="LANDSAT/LC08/C02/T1_L2",
                is_active=True,
                description="30 m thermal surface temperature via Landsat ST_B10 (°C).",
            ),
            LayerInfo(
                id="ndbi_change",
                name="NDBI Change (Built-up Expansion)",
                dataset="COPERNICUS/S2_SR_HARMONIZED",
                is_active=True,
                description="20 m built-up change via NDBI(end_year) - NDBI(start_year).",
            ),
            LayerInfo(
                id="lst_change",
                name="LST Change (Land Surface Temp Δ)",
                dataset="LANDSAT/LC08/C02/T1_L2",
                is_active=True,
                description="30 m thermal change via LST(end_year) - LST(start_year) (°C).",
            ),
        ]

    def get_metadata(self, req: TileRequest) -> MapMetadata:
        """Metadata for the requested query and layer."""
        return self.get_map_tiles(req).metadata

    def check_health(self) -> dict[str, Any]:
        """GEE initialisation and cache status."""
        status = self.authenticator.get_status()
        return {
            "status": ("healthy" if status.get("ee_initialized") else "degraded"),
            "gee_initialized": status.get("ee_initialized", False),
            "project_id": status.get("project_id"),
            "mode": status.get("mode"),
            "cache_entries": len(self._tile_cache),
        }
