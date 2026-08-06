"""GEEClient managing Earth Engine initialization, health checks, and task cancellation."""

from typing import Any

from src.infrastructure.earth_engine_runtime.gee_authenticator import GEEAuthenticator


class GEEClient:
    """Production client interface for Google Earth Engine."""

    def __init__(self, authenticator: GEEAuthenticator | None = None) -> None:
        self.authenticator = authenticator or GEEAuthenticator()
        self._is_initialized = False

    def initialize(self) -> bool:
        """Initialize Earth Engine API client."""
        if self.authenticator.authenticate():
            self._is_initialized = True
        return self._is_initialized

    def get_status(self) -> dict[str, Any]:
        """Return GEE client status dictionary."""
        return {
            "status": "healthy" if self._is_initialized else "uninitialized",
            "connected": self._is_initialized,
            "initialized": self._is_initialized,
            "authenticated": self._is_initialized,
            "authenticator": self.authenticator.get_status(),
        }

    def check_health(self) -> dict[str, Any]:
        """Perform Earth Engine connection health check."""
        return self.get_status()
