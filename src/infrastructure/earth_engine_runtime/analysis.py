"""Statistics and Visualization engines for raster indices (NDVI, NDBI, LST, NDWI)."""

from dataclasses import dataclass


@dataclass
class RasterStats:
    """Raster statistical metrics summary."""

    index_name: str
    mean_val: float
    std_dev: float
    min_val: float
    max_val: float


class StatisticsEngine:
    """Statistics engine computing raster reduction metrics."""

    @staticmethod
    def calculate_ndvi_stats(nir_band: list[float], red_band: list[float]) -> RasterStats:
        """Compute NDVI statistics from NIR and RED reflectance bands."""
        if not nir_band or not red_band:
            return RasterStats(
                index_name="NDVI", mean_val=0.0, std_dev=0.0, min_val=0.0, max_val=0.0
            )

        ndvi_vals = [
            (n - r) / (n + r)
            for n, r in zip(nir_band, red_band, strict=False)
            if (n + r) != 0
        ]
        if not ndvi_vals:
            return RasterStats(
                index_name="NDVI", mean_val=0.0, std_dev=0.0, min_val=0.0, max_val=0.0
            )

        mean_v = sum(ndvi_vals) / len(ndvi_vals)
        variance = sum((x - mean_v) ** 2 for x in ndvi_vals) / len(ndvi_vals)
        return RasterStats(
            index_name="NDVI",
            mean_val=round(mean_v, 4),
            std_dev=round(variance**0.5, 4),
            min_val=round(min(ndvi_vals), 4),
            max_val=round(max(ndvi_vals), 4),
        )

    @staticmethod
    def calculate_lst_celsius(st_b10: list[float]) -> list[float]:
        """Convert Landsat 8 ST_B10 digital numbers to Land Surface Temperature in Celsius."""
        # ST_B10 scale factor 0.00341802 + 149.0 (Kelvin) -> minus 273.15 (Celsius)
        return [(val * 0.00341802 + 149.0) - 273.15 for val in st_b10]


class VisualizationEngine:
    """Visualization engine rendering PNG preview color palettes."""

    @staticmethod
    def get_palette_for_index(index_name: str) -> list[str]:
        """Return standard color palette hex codes for raster index visualization."""
        name = index_name.upper()
        if name == "NDVI":
            return ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"]
        if name == "LST" or name == "LST_CELSIUS":
            return ["#0571b0", "#92c5de", "#f7f7f7", "#f4a582", "#ca0020"]
        if name == "NDWI":
            return ["#ffffcc", "#a1dab4", "#41b6c4", "#225ea8"]
        return ["#000000", "#ffffff"]
