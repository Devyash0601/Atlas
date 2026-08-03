"""Main FastAPI application entry point, middleware, and router setup."""

import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.interfaces.api.routers.health import router as health_router
from src.interfaces.api.schemas.health import ApiErrorDetail, ApiErrorResponse
from src.shared.config.settings import get_settings
from src.shared.exceptions.base import AtlasException
from src.shared.logging.logger import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Configure application startup and shutdown lifecycle events."""
    setup_logging()
    settings = get_settings()
    logger.info(
        "Starting ATLAS-EO FastAPI service",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
    yield
    logger.info("Stopping ATLAS-EO FastAPI service")


def create_app() -> FastAPI:
    """Initialize and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Autonomous Trustworthy Laboratory for Earth Observation Science",
        lifespan=lifespan,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID Correlation Middleware
    @app.middleware("http")
    async def add_request_correlation_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Global Exception Handler for Atlas Domain Errors
    @app.exception_handler(AtlasException)
    async def atlas_exception_handler(request: Request, exc: AtlasException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        logger.error("Domain exception occurred", error=exc.message, request_id=request_id)
        error_payload = ApiErrorResponse(
            success=False,
            error=ApiErrorDetail(
                code=exc.__class__.__name__,
                message=exc.message,
            ),
            request_id=request_id,
        )
        return JSONResponse(
            status_code=400,
            content=error_payload.model_dump(),
        )

    # Include API Routers under /api/v1
    app.include_router(health_router, prefix="/api/v1")

    return app


app = create_app()
