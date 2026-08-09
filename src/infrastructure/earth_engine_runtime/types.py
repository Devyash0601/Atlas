"""DTO type definitions for GEE tiles, requests, responses, layer metadata, and ROI geometries."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ROIInfo(BaseModel):
    """Region of Interest specification model."""

    type: str = Field(
        default="Polygon",
        description="Geometry type: Polygon, BoundingBox, PointRadius",
    )
    coordinates: list[Any] = Field(
        default_factory=list,
        description="Coordinates list or bounding box [min_lon, min_lat, max_lon, max_lat]",
    )


class TileRequest(BaseModel):
    """Parameters payload for requesting satellite tile URL."""

    lat: float = Field(default=17.3850, description="Center latitude")
    lng: float = Field(default=78.4867, description="Center longitude")
    zoom: int = Field(default=10, description="Zoom level")
    start_date: str = Field(default="2024-01-01", description="Start date (YYYY-MM-DD)")
    end_date: str = Field(default="2024-12-31", description="End date (YYYY-MM-DD)")
    cloud_threshold: float = Field(default=20.0, description="Maximum cloud pixel percentage")
    location_name: str | None = Field(default="Hyderabad", description="Location name")
    layer: str = Field(
        default="sentinel_rgb",
        description="Layer ID (sentinel_rgb, ndvi, ndwi, ndbi, lst)",
    )
    roi: dict[str, Any] | list[float] | None = Field(
        default=None,
        description="GeoJSON geometry or bounding box",
    )

    @model_validator(mode="after")
    def validate_parameters(self) -> "TileRequest":
        """Validate date range and cloud threshold."""
        if not (0.0 <= self.cloud_threshold <= 100.0):
            raise ValueError(
                f"cloud_threshold must be between 0.0 and 100.0, got {self.cloud_threshold}."
            )
        try:
            start_dt = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(self.end_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(
                f"Invalid date format: start_date '{self.start_date}' or "
                f"end_date '{self.end_date}'. Expected YYYY-MM-DD."
            ) from exc

        if start_dt >= end_dt:
            raise ValueError(
                f"start_date '{self.start_date}' must be earlier than end_date '{self.end_date}'."
            )
        return self


class MapMetadata(BaseModel):
    """Metadata details for generated satellite imagery tile."""

    dataset: str = Field(
        default="COPERNICUS/S2_SR_HARMONIZED",
        description="Earth Observation dataset ID",
    )
    collection_name: str = Field(
        default="Sentinel-2 Surface Reflectance",
        description="Human-readable collection name",
    )
    date_range: str = Field(default="2024-01-01 to 2024-12-31", description="Filtered date range")
    cloud_threshold_pct: float = Field(
        default=20.0,
        description="Cloud threshold filter percentage",
    )
    bands: list[str] = Field(
        default_factory=lambda: ["B4", "B3", "B2"],
        description="Band combination",
    )
    resolution_meters: int = Field(default=10, description="Spatial resolution in meters")
    projection: str = Field(default="EPSG:4326", description="Map projection CRS")
    image_id: str = Field(default="S2_MEDIAN_COMPOSITE", description="Composite image identifier")
    index: str | None = Field(default=None, description="Index name (e.g. NDVI)")
    formula: str | None = Field(default=None, description="Mathematical index formula")
    palette: list[str] | None = Field(
        default=None,
        description="Visualization palette hex codes",
    )
    vis_min: float | None = Field(default=None, description="Visualization minimum value")
    vis_max: float | None = Field(default=None, description="Visualization maximum value")


class TileResponse(BaseModel):
    """Response payload containing generated tile URL and image metadata."""

    success: bool = Field(default=True, description="Request execution status")
    mapid: str = Field(..., description="Earth Engine map ID token")
    token: str = Field(..., description="Earth Engine session token")
    tile_url: str = Field(
        ...,
        description="Leaflet formatted tile URL template ({z}/{x}/{y})",
    )
    metadata: MapMetadata = Field(..., description="Satellite metadata summary")


class LayerInfo(BaseModel):
    """Map layer description model."""

    id: str = Field(..., description="Layer identifier")
    name: str = Field(..., description="Display name")
    dataset: str = Field(..., description="Source GEE dataset")
    is_active: bool = Field(..., description="Whether layer is active in current release")
    description: str = Field(..., description="Layer description")


class ScatterPoint(BaseModel):
    """Spatially paired observation point (ΔNDBI, ΔLST)."""

    delta_ndbi: float = Field(..., description="Resampled 30m ΔNDBI value")
    delta_lst: float = Field(..., description="Native 30m ΔLST thermal change (°C)")


class VariableStats(BaseModel):
    """Descriptive statistics for a spatial change index."""

    native_resolution_m: int = Field(..., description="Native sensor spatial resolution")
    mean_change: float = Field(..., description="Mean spatial change value")
    std_change: float = Field(..., description="Standard deviation of spatial change")


class CorrelationMetrics(BaseModel):
    """Statistical correlation results for paired observations."""

    pearson_r: float = Field(..., description="Pearson correlation coefficient r")
    pearson_p_value: float | None = Field(default=None, description="Two-tailed Pearson p-value")
    spearman_rho: float = Field(..., description="Spearman rank correlation coefficient rho")
    spearman_p_value: float | None = Field(default=None, description="Two-tailed Spearman p-value")


class RegressionMetrics(BaseModel):
    """Ordinary Least Squares (OLS) linear regression model parameters."""

    slope: float = Field(..., description="Regression slope beta_1 (°C per NDBI unit)")
    intercept: float = Field(..., description="Regression intercept beta_0 (°C)")
    r_squared: float = Field(..., description="Coefficient of determination R^2")


class RelationshipMetadata(BaseModel):
    """Metadata describing the spatial relationship methodology and parameters."""

    baseline_year: int = Field(default=2016, description="Baseline observation year")
    end_year: int = Field(default=2025, description="Endpoint observation year")
    ndbi_dataset: str = Field(default="COPERNICUS/S2_SR_HARMONIZED")
    ndbi_native_resolution_m: int = Field(default=20)
    lst_dataset: str = Field(default="LANDSAT/LC08/C02/T1_L2")
    lst_native_resolution_m: int = Field(default=30)
    analysis_crs: str = Field(default="EPSG:32644", description="Projected metric CRS")
    analysis_grid_m: int = Field(default=30, description="Common analysis grid (m)")
    ndbi_resampling: str = Field(default="bilinear", description="NDBI 30m resampling")
    sampling_method: str = Field(default="controlled random spatial sample")
    seed: int = Field(default=42, description="Deterministic random sampling seed")
    cloud_threshold_pct: float = Field(default=20.0, description="Cloud threshold filter pct")
    roi: list[float] = Field(..., description="Bounding box ROI [lons, lats]")


class RelationshipAnalysisResponse(BaseModel):
    """Response payload for ΔNDBI ↔ ΔLST spatial relationship analysis."""

    location: str = Field(..., description="Study location name")
    baseline_year: int = Field(..., description="Baseline year")
    end_year: int = Field(..., description="Endpoint year")
    cloud_threshold: float = Field(..., description="Cloud threshold percentage")
    analysis_resolution_m: int = Field(default=30, description="Common analysis grid resolution")
    sample_size: int = Field(..., description="Number of valid paired spatial observations")
    ndbi: VariableStats = Field(..., description="NDBI change spatial statistics")
    lst: VariableStats = Field(..., description="LST change spatial statistics")
    correlation: CorrelationMetrics = Field(..., description="Pearson and Spearman correlation")
    regression: RegressionMetrics = Field(..., description="OLS linear regression parameters")
    scatter_points: list[ScatterPoint] = Field(..., description="Visualization scatter points")
    raw_sample: list[ScatterPoint] = Field(
        default_factory=list,
        description="Full precision paired observations for independent validation",
    )
    metadata: RelationshipMetadata = Field(..., description="Methodology metadata")
    interpretation: str = Field(..., description="Automated non-causal statistical interpretation")
    autocorrelation_warning: str = Field(..., description="Spatial autocorrelation disclosure note")
