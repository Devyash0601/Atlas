"""Production unit tests for GEE Runtime engine."""

from unittest.mock import MagicMock, patch

from src.infrastructure.earth_engine_runtime.exceptions import (
    AuthenticationError,
    DatasetUnavailableError,
    InvalidROIError,
    TileGenerationError,
)
from src.infrastructure.earth_engine_runtime.gee_authenticator import (
    GEEAuthenticator,
)

_EE_PATCH = "src.infrastructure.earth_engine_runtime.gee_authenticator.ee"


def test_gee_authenticator_and_client() -> None:
    """Test GEE authenticator initialization and health check."""
    mock_ee = MagicMock()
    with patch(_EE_PATCH, mock_ee):
        mock_ee.ServiceAccountCredentials.return_value = MagicMock()
        mock_ee.Initialize.return_value = None

        auth = GEEAuthenticator(mode="service_account", project_id="test_project")
        assert auth.authenticate() is True
        assert auth.validate_connection() is True
        auth._token_expiry_timestamp = 0.0

        # Reset _ee_initialized so refresh re-authenticates
        GEEAuthenticator._ee_initialized = False
        auth.refresh_token_if_needed()

        status = auth.get_status()
        assert status["is_authenticated"] is True
        assert status["project_id"] in ("test_project", "ee-devkomiya")

        from src.infrastructure.earth_engine_runtime.gee_runtime import GEEClient

        client = GEEClient(authenticator=auth)
        assert client.initialize() is True
        health = client.check_health()
        assert health["status"] == "healthy"


def test_typed_exceptions_instantiation() -> None:
    """Test custom exception classes."""
    e1 = AuthenticationError("Auth failed")
    assert str(e1) == "Auth failed"

    e2 = InvalidROIError("Bad ROI")
    assert str(e2) == "Bad ROI"

    e3 = TileGenerationError("Tile error")
    assert str(e3) == "Tile error"

    e4 = DatasetUnavailableError("Dataset missing")
    assert str(e4) == "Dataset missing"
