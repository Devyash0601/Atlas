"""FastAPI router for research spatial change analysis and ΔNDBI ↔ ΔLST relationship analysis."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.infrastructure.earth_engine_runtime.exceptions import InvalidROIError
from src.infrastructure.earth_engine_runtime.gee_service import GEEService
from src.infrastructure.earth_engine_runtime.types import (
    RelationshipAnalysisResponse,
    TileRequest,
)

router = APIRouter(prefix="/analysis", tags=["Research Change & Relationship Analysis"])

_gee_service: GEEService | None = None


def get_gee_service() -> GEEService:
    """Lazy singleton instantiation of GEEService."""
    global _gee_service
    if _gee_service is None:
        _gee_service = GEEService()
    return _gee_service


@router.get("/change")
def get_change_analysis(
    location: str = Query("Hyderabad", description="Location name (e.g. Hyderabad)"),
    start_year: int = Query(2016, description="Baseline year"),
    end_year: int = Query(2025, description="Endpoint year"),
    cloud: float = Query(20.0, description="Cloud cover threshold (0.0 to 100.0)"),
) -> dict[str, Any]:
    """Calculate 2016 vs 2025 spatial change rasters (ΔNDBI and ΔLST) inside Earth Engine."""
    if start_year >= end_year:
        raise HTTPException(
            status_code=400,
            detail=f"start_year ({start_year}) must be earlier than end_year ({end_year}).",
        )
    if not (0.0 <= cloud <= 100.0):
        raise HTTPException(
            status_code=400,
            detail=f"cloud_threshold must be between 0.0 and 100.0, got {cloud}.",
        )

    try:
        service = get_gee_service()

        req_ndbi = TileRequest(
            location_name=location,
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-12-31",
            cloud_threshold=cloud,
            layer="ndbi_change",
        )
        resp_ndbi = service.get_map_tiles(req_ndbi)

        req_lst = TileRequest(
            location_name=location,
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-12-31",
            cloud_threshold=cloud,
            layer="lst_change",
        )
        resp_lst = service.get_map_tiles(req_lst)

        return {
            "location": location,
            "baseline_year": start_year,
            "end_year": end_year,
            "cloud_threshold": cloud,
            "layers": {
                "ndbi_change": resp_ndbi.model_dump(),
                "lst_change": resp_lst.model_dump(),
            },
        }
    except (ValueError, InvalidROIError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate GEE spatial change analysis: {exc}",
        ) from exc


@router.get("/relationship", response_model=RelationshipAnalysisResponse)
def get_relationship_analysis(
    location: str = Query("Hyderabad", description="Location name (e.g. Hyderabad)"),
    start_year: int = Query(2016, description="Baseline year"),
    end_year: int = Query(2025, description="Endpoint year"),
    cloud: float = Query(20.0, description="Cloud cover threshold (0.0 to 100.0)"),
    sample_size: int = Query(10000, description="Number of spatial sampling pixels (500 to 50000)"),
    seed: int = Query(42, description="Deterministic random sampling seed"),
) -> RelationshipAnalysisResponse:
    """Perform ΔNDBI ↔ ΔLST spatial relationship analysis using paired GEE spatial observations."""
    if start_year >= end_year:
        raise HTTPException(
            status_code=400,
            detail=f"start_year ({start_year}) must be earlier than end_year ({end_year}).",
        )
    if not (0.0 <= cloud <= 100.0):
        raise HTTPException(
            status_code=400,
            detail=f"cloud_threshold must be between 0.0 and 100.0, got {cloud}.",
        )
    if not (100 <= sample_size <= 50000):
        raise HTTPException(
            status_code=400,
            detail=f"sample_size must be between 100 and 50000, got {sample_size}.",
        )

    try:
        service = get_gee_service()
        bounds = service.validate_roi(None, location_name=location)

        return service.get_relationship_analysis(
            bounds=bounds,
            start_year=start_year,
            end_year=end_year,
            cloud_threshold=cloud,
            sample_size=sample_size,
            seed=seed,
            location_name=location,
        )
    except (ValueError, InvalidROIError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate GEE spatial relationship analysis: {exc}",
        ) from exc
