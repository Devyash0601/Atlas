"""Tile generation service wrapping Earth Engine getMapId() for Leaflet maps."""

import hashlib
from typing import Any

import ee

from src.infrastructure.earth_engine_runtime.exceptions import (
    TileGenerationError,
)
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)

# Sentinel value returned by gee_service when ee is not initialised
_TEST_ONLY_PLACEHOLDER = "S2_RGB_MEDIAN_COMPOSITE"


class TileService:
    """Generates map IDs and Leaflet-compatible tile URLs via ee.Image.getMapId()."""

    @staticmethod
    def generate_tile(
        image: Any,
        vis_params: dict[str, Any] | None = None,
        layer_name: str = "Sentinel-2 RGB",
    ) -> dict[str, str]:
        """Convert an ee.Image into a Leaflet tile URL template.

        If *image* is a real ``ee.Image`` or mock with ``getMapId()``, calls
        ``getMapId()`` and returns the authenticated tile URL.

        If *image* is the test-only placeholder string, returns a
        clearly-marked simulated URL (unit-test path only).

        Raises:
            TileGenerationError: When ``getMapId()`` fails on a real image.
        """
        if vis_params is None:
            vis_params = {
                "bands": ["B4", "B3", "B2"],
                "min": 0,
                "max": 3000,
            }

        # ── Real ee.Image path (or mock image with getMapId) ───────
        is_ee_image = isinstance(image, ee.Image) or (
            hasattr(image, "getMapId") and callable(image.getMapId)
        )

        if is_ee_image and image != _TEST_ONLY_PLACEHOLDER:
            try:
                map_id_dict = image.getMapId(vis_params)
                mapid = map_id_dict.get("mapid", "")
                token = map_id_dict.get("token", "")

                tile_fetcher = map_id_dict.get("tile_fetcher")
                if tile_fetcher and hasattr(tile_fetcher, "url_format"):
                    tile_url = tile_fetcher.url_format
                else:
                    tile_url = (
                        f"https://earthengine.googleapis.com/v1/{mapid}/tiles/{{z}}/{{x}}/{{y}}"
                    )

                logger.info(
                    "Generated REAL GEE tile URL via getMapId()",
                    layer_name=layer_name,
                    mapid=mapid[:16] if mapid else "?",
                )
                return {
                    "mapid": mapid,
                    "token": token,
                    "tile_url": tile_url,
                }

            except Exception as exc:
                logger.error(
                    "ee.Image.getMapId() FAILED",
                    error=str(exc),
                    layer_name=layer_name,
                )
                raise TileGenerationError(f"getMapId() failed: {exc}") from exc

        # ── Test-only simulated fallback ─────────────────────────
        if image == _TEST_ONLY_PLACEHOLDER:
            hash_seed = f"{layer_name}_{vis_params.get('bands')}"
            digest = hashlib.md5(hash_seed.encode("utf-8")).hexdigest()[:16]
            mock_mapid = f"projects/earthengine-legacy/maps/{digest}"
            mock_url = f"https://earthengine.googleapis.com/v1/{mock_mapid}/tiles/{{z}}/{{x}}/{{y}}"
            logger.warning(
                "Using TEST-ONLY simulated tile (not real GEE)",
                layer_name=layer_name,
            )
            return {
                "mapid": mock_mapid,
                "token": f"tok_{digest}",
                "tile_url": mock_url,
            }

        # ── Unknown image type ───────────────────────────────────
        raise TileGenerationError(
            f"Unsupported image type: {type(image).__name__}. Expected ee.Image or test placeholder"
        )
