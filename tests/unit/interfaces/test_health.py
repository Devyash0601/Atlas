"""Unit tests for FastAPI health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_success(async_client: AsyncClient) -> None:
    """Verify health endpoint returns HTTP 200 with standard envelope structure."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert "data" in payload
    assert payload["data"]["status"] == "healthy"
    assert "version" in payload["data"]
    assert payload["data"]["environment"] is not None
    assert isinstance(payload["data"]["uptime_seconds"], (int, float))
    assert payload["request_id"] != ""
