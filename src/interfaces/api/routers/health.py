"""Health check API router implementation."""

import time
import uuid

from fastapi import APIRouter

from src.interfaces.api.dependencies.container import SettingsDep, get_start_time
from src.interfaces.api.schemas.health import ApiResponse, HealthData

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=ApiResponse[HealthData],
    summary="Service Health Check",
    description="Check overall backend readiness, environment, and uptime metrics.",
)
async def check_health(settings: SettingsDep) -> ApiResponse[HealthData]:
    """Retrieve service status, version, and uptime."""
    uptime = time.time() - get_start_time()
    health_data = HealthData(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(uptime, 2),
    )
    return ApiResponse(
        success=True,
        data=health_data,
        message="Service operates normally",
        request_id=str(uuid.uuid4()),
    )
