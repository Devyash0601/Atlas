"""FastAPI REST router for Earth Engine map tiles, layers, metadata, and health."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, HTTPException, Query, status

from src.infrastructure.earth_engine_runtime.exceptions import (
    InvalidROIError,
)
from src.infrastructure.earth_engine_runtime.types import (
    LayerInfo,
    MapMetadata,
    TileRequest,
    TileResponse,
)
from src.shared.logging.logger import get_logger

if TYPE_CHECKING:
    from src.infrastructure.earth_engine_runtime.gee_service import (
        GEEService,
    )

logger = get_logger(__name__)

router = APIRouter(prefix="/map", tags=["Earth Engine Map Services"])

# Lazy singleton — instantiated on first request, not at import time.
_gee_service: GEEService | None = None


def _get_gee_service() -> GEEService:
    """Lazily initialise the GEEService singleton.

    This avoids calling ee.Initialize() at module-import time,
    which would break unit tests and any startup without GEE
    credentials configured.
    """
    global _gee_service
    if _gee_service is None:
        from src.infrastructure.earth_engine_runtime.gee_service import (
            GEEService,
        )

        try:
            _gee_service = GEEService()
        except RuntimeError as exc:
            logger.error("GEE service init failed", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Earth Engine unavailable: {exc}",
            ) from exc
    return _gee_service


@router.get(
    "/layers",
    response_model=list[LayerInfo],
    status_code=status.HTTP_200_OK,
    summary="List Available Map Layers",
    description="Retrieve available Earth Observation map layers.",
)
async def list_layers() -> list[LayerInfo]:
    """Retrieve available map layers list."""
    return _get_gee_service().get_layers()


@router.get(
    "/tiles",
    response_model=TileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Map Tile URL for Layer",
    description="Generate a Leaflet tile URL for Sentinel-2 RGB or NDVI rasters.",
)
async def get_map_tiles(
    lat: float = Query(17.3850, description="Center latitude"),
    lng: float = Query(78.4867, description="Center longitude"),
    zoom: int = Query(10, description="Zoom level"),
    start_date: str = Query("2024-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: str = Query("2024-12-31", description="End date (YYYY-MM-DD)"),
    cloud: float = Query(20.0, description="Maximum cloud pixel percentage"),
    location: str | None = Query("Hyderabad", description="Location name"),
    layer: str = Query(
        "sentinel_rgb",
        description="Layer ID: sentinel_rgb, ndvi, ndwi, ndbi, or lst",
    ),
) -> TileResponse:
    """Generate map tile URL and metadata for specified layer and parameters."""
    try:
        request_dto = TileRequest(
            lat=lat,
            lng=lng,
            zoom=zoom,
            start_date=start_date,
            end_date=end_date,
            cloud_threshold=cloud,
            location_name=location,
            layer=layer,
        )
        return _get_gee_service().get_map_tiles(request_dto)
    except (ValueError, InvalidROIError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/metadata",
    response_model=MapMetadata,
    status_code=status.HTTP_200_OK,
    summary="Get Imagery Metadata Summary",
    description="Retrieve Earth Observation dataset metadata.",
)
async def get_map_metadata(
    start_date: str = Query("2024-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: str = Query("2024-12-31", description="End date (YYYY-MM-DD)"),
    cloud: float = Query(20.0, description="Maximum cloud pixel percentage"),
    location: str | None = Query("Hyderabad", description="Location name"),
    layer: str = Query(
        "sentinel_rgb",
        description="Layer ID: sentinel_rgb, ndvi, ndwi, ndbi, or lst",
    ),
) -> MapMetadata:
    """Retrieve satellite imagery metadata summary."""
    try:
        request_dto = TileRequest(
            start_date=start_date,
            end_date=end_date,
            cloud_threshold=cloud,
            location_name=location,
            layer=layer,
        )
        return _get_gee_service().get_metadata(request_dto)
    except (ValueError, InvalidROIError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/health",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="GEE Service Health Check",
    description="Check Earth Engine initialisation and cache.",
)
async def get_map_health() -> dict[str, Any]:
    """Return Earth Engine service health status."""
    return _get_gee_service().check_health()
