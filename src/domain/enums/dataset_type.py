"""Dataset and satellite source domain enums."""

from enum import StrEnum


class SatelliteType(StrEnum):
    """Supported satellite constellations."""

    LANDSAT_C2 = "landsat_collection_2"
    SENTINEL_2 = "sentinel_2"
    MODIS = "modis"


class DatasetType(StrEnum):
    """Types of Earth Observation datasets."""

    OPTICAL_SURFACE_REFLECTANCE = "optical_surface_reflectance"
    LAND_SURFACE_TEMPERATURE = "land_surface_temperature"
    VEGETATION_INDEX = "vegetation_index"
    BUILD_UP_INDEX = "build_up_index"
