"""Pydantic schemas for health endpoint and API envelope responses."""

from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class HealthData(BaseModel):
    """System health metrics and environment state."""

    status: str = Field(default="healthy", description="Overall health status")
    version: str = Field(description="Application semantic version")
    environment: str = Field(description="Deployment environment name")
    uptime_seconds: float = Field(description="Service uptime in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "uptime_seconds": 42.5,
            }
        }
    )


class ApiResponse[T](BaseModel):
    """Standard success API response envelope."""

    success: bool = Field(default=True, description="Indicates request success status")
    data: T = Field(description="Response data payload")
    message: str = Field(default="", description="Optional context message")
    request_id: str = Field(default="", description="Unique request tracing correlation ID")


class ApiErrorDetail(BaseModel):
    """Detailed error object representation."""

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")


class ApiErrorResponse(BaseModel):
    """Standard error API response envelope."""

    success: bool = Field(default=False, description="Indicates request failure status")
    error: ApiErrorDetail = Field(description="Error details payload")
    request_id: str = Field(default="", description="Unique request tracing correlation ID")
