"""Main FastAPI application entry point, middleware, and router setup."""

import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.infrastructure.earth_engine_runtime.exceptions import (
    AuthenticationError,
    DatasetUnavailableError,
    InvalidROIError,
    TileGenerationError,
)
from src.interfaces.api.routers.analysis import router as analysis_router
from src.interfaces.api.routers.health import router as health_router
from src.interfaces.api.routers.map import router as map_router
from src.interfaces.api.routers.research import router as research_router
from src.interfaces.api.schemas.health import ApiErrorDetail, ApiErrorResponse
from src.shared.config.settings import get_settings
from src.shared.exceptions.base import AtlasException, NotFoundException
from src.shared.logging.logger import get_logger, setup_logging

# Load active environment variables
load_dotenv()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator[None]:
    """Lifespan context manager for startup and shutdown events."""
    setup_logging()
    settings = get_settings()
    logger.info(
        "Starting ATLAS-EO FastAPI service",
        version=app_instance.version,
        environment=settings.ENVIRONMENT,
    )
    yield
    logger.info("Stopping ATLAS-EO FastAPI service")


app = FastAPI(
    title="ATLAS-EO Research API Engine",
    description="REST API for Earth Engine Satellite Imagery & Research Pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Inject X-Correlation-ID tracing header into request state and response headers."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Global Exception Handlers
@app.exception_handler(AtlasException)
async def atlas_exception_handler(request: Request, exc: AtlasException) -> JSONResponse:
    """Handle custom application exceptions cleanly."""
    status_code = getattr(exc, "status_code", 400)
    error_resp = ApiErrorResponse(
        error=ApiErrorDetail(
            code=exc.__class__.__name__,
            message=str(exc),
        )
    )
    return JSONResponse(status_code=status_code, content=error_resp.model_dump())


@app.exception_handler(InvalidROIError)
@app.exception_handler(TileGenerationError)
@app.exception_handler(AuthenticationError)
@app.exception_handler(DatasetUnavailableError)
async def gee_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle GEE domain runtime exceptions cleanly."""
    status_code = 400 if isinstance(exc, InvalidROIError) else 500
    error_resp = ApiErrorResponse(
        error=ApiErrorDetail(
            code=exc.__class__.__name__,
            message=str(exc),
        )
    )
    return JSONResponse(status_code=status_code, content=error_resp.model_dump())


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """Handle 404 Not Found errors cleanly."""
    error_resp = ApiErrorResponse(
        error=ApiErrorDetail(
            code="NOT_FOUND",
            message=str(exc),
        )
    )
    return JSONResponse(status_code=404, content=error_resp.model_dump())


# Register API Routers under /api/v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")
app.include_router(map_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
