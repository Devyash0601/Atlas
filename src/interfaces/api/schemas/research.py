"""Pydantic schemas for research API requests, responses, project summaries, and reports."""

from typing import Any

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Payload specification for triggering autonomous research pipeline."""

    question: str = Field(
        ...,
        description="Natural language scientific research question",
        json_schema_extra={"example": "Urban expansion and land surface temperature"},
    )
    location: str | None = Field(
        None,
        description="Geographic region of interest",
        json_schema_extra={"example": "Hyderabad"},
    )
    start_date: str | None = Field(
        None,
        description="ISO format start date (YYYY-MM-DD)",
        json_schema_extra={"example": "2016-01-01"},
    )
    end_date: str | None = Field(
        None,
        description="ISO format end date (YYYY-MM-DD)",
        json_schema_extra={"example": "2025-12-31"},
    )
    dataset_preference: str | None = Field(
        None,
        description="Preferred Earth Observation satellite dataset ID",
        json_schema_extra={"example": "COPERNICUS/S2_SR_HARMONIZED"},
    )


class ResearchResponse(BaseModel):
    """Response payload returned after starting or completing research pipeline."""

    project_id: str = Field(..., description="Unique research project identifier")
    question: str = Field(..., description="Original research question")
    location: str | None = Field(None, description="Study region")
    status: str = Field(..., description="Pipeline execution status")
    project_dir: str = Field(..., description="Absolute path to generated project directory")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Pipeline execution metrics")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")


class ProjectSummary(BaseModel):
    """Summary model for listing executed research projects."""

    project_id: str = Field(..., description="Unique project ID")
    question: str = Field(..., description="Research question")
    location: str | None = Field(None, description="Study region")
    status: str = Field(..., description="Execution status")
    created_at: str = Field(..., description="Creation timestamp")


class ReportResponse(BaseModel):
    """Publication report content and metadata model."""

    project_id: str = Field(..., description="Unique project ID")
    question: str = Field(..., description="Research question")
    report_content: str = Field(..., description="Generated markdown report body")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Publication metadata")
