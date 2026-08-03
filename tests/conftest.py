"""Global Pytest fixtures and configuration."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.interfaces.api.main import app


@pytest.fixture
async def async_client():
    """Asynchronous HTTP test client fixture for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
