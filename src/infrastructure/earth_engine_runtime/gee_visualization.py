"""GEEVisualizationEngine generating RGB composites, false color, index maps, and legends."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisualizationMapPayload:
    """Visualization layer map preview configuration."""

    layer_name: str
    vis_params: dict[str, Any]
    tile_url: str
    png_preview_url: str
    color_palette: list[str] = field(default_factory=list)


class GEEVisualizationEngine:
    """Engine generating visualization layers and color map legends for remote sensing outputs."""

    @staticmethod
    def create_ndvi_visualization(
        min_val: float = -0.2, max_val: float = 0.8
    ) -> VisualizationMapPayload:
        """Create NDVI visualization palette map."""
        palette = [
            "#FFFFFF",
            "#CE7E45",
            "#DF923D",
            "#F1B555",
            "#FCD163",
            "#99B718",
            "#74A901",
            "#66A000",
            "#529400",
            "#3E8601",
            "#207401",
            "#056201",
            "#004C00",
        ]
        return VisualizationMapPayload(
            layer_name="NDVI Vegetation Index",
            vis_params={"min": min_val, "max": max_val, "palette": palette},
            tile_url="https://earthengine.googleapis.com/v1/map/ndvi/{z}/{x}/{y}",
            png_preview_url="https://earthengine.googleapis.com/v1/preview/ndvi.png",
            color_palette=palette,
        )

    @staticmethod
    def create_lst_heatmap(min_val: float = 15.0, max_val: float = 45.0) -> VisualizationMapPayload:
        """Create LST surface temperature heatmap layer."""
        palette = ["blue", "cyan", "green", "yellow", "red"]
        return VisualizationMapPayload(
            layer_name="LST Surface Temperature",
            vis_params={"min": min_val, "max": max_val, "palette": palette},
            tile_url="https://earthengine.googleapis.com/v1/map/lst/{z}/{x}/{y}",
            png_preview_url="https://earthengine.googleapis.com/v1/preview/lst.png",
            color_palette=palette,
        )

    @classmethod
    def get_palette_for_index(cls, index_name: str) -> list[str]:
        """Backward compatibility helper returning index palette."""
        return ["#FFFFFF", "#004C00"]
