"""Earth Observation dataset catalog specifications for Landsat, Sentinel-2, and MODIS."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class DatasetSpec:
    """Specification for Earth Observation satellite dataset."""

    collection_id: str
    name: str
    satellite: str
    spatial_resolution_meters: float
    bands: list[str]


class DatasetCatalog:
    """Catalog of supported satellite collections."""

    DATASETS: ClassVar[dict[str, DatasetSpec]] = {
        "landsat_c2": DatasetSpec(
            collection_id="LANDSAT/LC08/C02/T1_L2",
            name="Landsat Collection 2 Tier 1 Level 2",
            satellite="Landsat 8/9",
            spatial_resolution_meters=30.0,
            bands=["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10"],
        ),
        "sentinel_2": DatasetSpec(
            collection_id="COPERNICUS/S2_SR_HARMONIZED",
            name="Sentinel-2 Surface Reflectance Harmonized",
            satellite="Sentinel-2A/2B",
            spatial_resolution_meters=10.0,
            bands=["B2", "B3", "B4", "B8", "B11", "B12"],
        ),
        "modis": DatasetSpec(
            collection_id="MODIS/061/MOD11A1",
            name="MODIS Land Surface Temperature/Emissivity Daily 1km",
            satellite="Terra MODIS",
            spatial_resolution_meters=1000.0,
            bands=["LST_Day_1km", "QC_Day"],
        ),
    }

    @classmethod
    def get_dataset(cls, alias: str) -> DatasetSpec:
        """Retrieve dataset spec by alias key."""
        if alias not in cls.DATASETS:
            msg = (
                f"Dataset alias '{alias}' not found in catalog. "
                f"Available: {list(cls.DATASETS.keys())}"
            )
            raise KeyError(msg)
        return cls.DATASETS[alias]
