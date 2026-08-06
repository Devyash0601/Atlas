"""GEEDatasetCatalog supporting Sentinel-2, Landsat, MODIS, DEM, ERA5, CHIRPS, and Dynamic World."""

from dataclasses import dataclass, field
from typing import Any, ClassVar

from src.infrastructure.earth_engine_runtime.gee_error_handler import EEDatasetUnavailable


@dataclass(frozen=True)
class DatasetMetadata:
    """Earth Engine satellite dataset metadata entry."""

    asset_id: str
    name: str
    bands: list[str]
    resolution_meters: float
    temporal_coverage: str
    provider: str
    cloud_mask_strategy: str
    recommended_indices: list[str] = field(default_factory=list)

    @property
    def satellite(self) -> str:
        """Backward compatibility satellite attribute."""
        if "Sentinel" in self.name:
            return "Sentinel-2"
        if "Landsat" in self.name:
            return "Landsat 8/9"
        return self.provider


class GEEDatasetCatalog:
    """Production Earth Engine Dataset Catalog."""

    CATALOG: ClassVar[dict[str, DatasetMetadata]] = {
        "COPERNICUS/S2_SR_HARMONIZED": DatasetMetadata(
            asset_id="COPERNICUS/S2_SR_HARMONIZED",
            name="Sentinel-2 MSI Surface Reflectance",
            bands=["B2", "B3", "B4", "B8", "B11", "B12", "QA60"],
            resolution_meters=10.0,
            temporal_coverage="2015-06-23 to present",
            provider="ESA / Copernicus",
            cloud_mask_strategy="s2cloudless",
            recommended_indices=["NDVI", "NDWI", "NDBI"],
        ),
        "LANDSAT/LC08/C02/T1_L2": DatasetMetadata(
            asset_id="LANDSAT/LC08/C02/T1_L2",
            name="Landsat 8 Collection 2 Tier 1 L2",
            bands=["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10", "QA_PIXEL"],
            resolution_meters=30.0,
            temporal_coverage="2013-04-11 to present",
            provider="USGS / NASA",
            cloud_mask_strategy="qa_pixel_mask",
            recommended_indices=["NDVI", "LST", "NDBI"],
        ),
        "LANDSAT/LC09/C02/T1_L2": DatasetMetadata(
            asset_id="LANDSAT/LC09/C02/T1_L2",
            name="Landsat 9 Collection 2 Tier 1 L2",
            bands=["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10", "QA_PIXEL"],
            resolution_meters=30.0,
            temporal_coverage="2021-10-31 to present",
            provider="USGS / NASA",
            cloud_mask_strategy="qa_pixel_mask",
            recommended_indices=["NDVI", "LST"],
        ),
        "USGS/SRTM90_V4": DatasetMetadata(
            asset_id="USGS/SRTM90_V4",
            name="SRTM Digital Elevation Data 90m",
            bands=["elevation"],
            resolution_meters=90.0,
            temporal_coverage="2000-02-11 to 2000-02-22",
            provider="USGS",
            cloud_mask_strategy="none",
            recommended_indices=["Slope", "Aspect"],
        ),
        "ECMWF/ERA5_LAND/MONTHLY_AGGR": DatasetMetadata(
            asset_id="ECMWF/ERA5_LAND/MONTHLY_AGGR",
            name="ERA5-Land Monthly Aggregated",
            bands=["temperature_2m", "total_precipitation_sum"],
            resolution_meters=11132.0,
            temporal_coverage="1950-01-01 to present",
            provider="ECMWF / Copernicus",
            cloud_mask_strategy="none",
            recommended_indices=["ClimateStats"],
        ),
        "GOOGLE/DYNAMICWORLD/V1": DatasetMetadata(
            asset_id="GOOGLE/DYNAMICWORLD/V1",
            name="Dynamic World V1 Land Cover",
            bands=[
                "label",
                "water",
                "trees",
                "grass",
                "flooded_vegetation",
                "crops",
                "shrub_and_scrub",
                "built",
                "bare",
                "snow_and_ice",
            ],
            resolution_meters=10.0,
            temporal_coverage="2015-06-23 to present",
            provider="Google / World Resources Institute",
            cloud_mask_strategy="none",
            recommended_indices=["LandCoverStats"],
        ),
    }

    def get_dataset(self_or_asset: Any, asset_id: str | None = None) -> DatasetMetadata:
        """Retrieve dataset metadata by asset ID or short name."""
        if asset_id is not None:
            target = asset_id
        elif isinstance(self_or_asset, str):
            target = self_or_asset
        else:
            target = ""
        if target == "landsat_c2":
            target = "LANDSAT/LC08/C02/T1_L2"
        elif target == "sentinel2_sr":
            target = "COPERNICUS/S2_SR_HARMONIZED"

        if target not in GEEDatasetCatalog.CATALOG:
            raise EEDatasetUnavailable(f"Dataset asset ID '{target}' is not in GEEDatasetCatalog.")
        return GEEDatasetCatalog.CATALOG[target]

    def list_datasets(self) -> list[DatasetMetadata]:
        """Return list of all registered dataset metadata entries."""
        return list(self.CATALOG.values())


# Backward compatibility alias
DatasetCatalog = GEEDatasetCatalog
