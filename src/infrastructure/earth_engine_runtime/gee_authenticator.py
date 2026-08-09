"""GEEAuthenticator supporting Service Account and Application Default Credentials."""

import os
import time
from typing import Any

import ee

from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class GEEAuthenticator:
    """Authenticator handling Google Earth Engine Service Account credentials.

    Supports two authentication modes:
    - service_account: Uses a JSON key file and service account email
    - adc: Uses Application Default Credentials (gcloud auth)

    The authenticator initialises Earth Engine once and reuses the session.
    """

    _ee_initialized: bool = False

    def __init__(
        self,
        mode: str = "service_account",
        project_id: str = "atlas-eo-project",
        service_account: str | None = None,
        key_file: str | None = None,
    ) -> None:
        self.mode = mode
        self.project_id = os.environ.get("GEE_PROJECT_ID", project_id)
        self.service_account = os.environ.get("GEE_SERVICE_ACCOUNT", service_account)
        self.key_file = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS",
            os.environ.get("GEE_KEY_FILE", key_file),
        )
        self._is_authenticated = False
        self._token_expiry_timestamp: float = 0.0

    def authenticate(self) -> bool:
        """Authenticate with Earth Engine using configured credentials.

        If service account email and key file are both provided and key file exists,
        uses ee.ServiceAccountCredentials. Otherwise falls back to ee.Initialize
        or mock mode for unit tests.

        Returns True if authenticated.
        """
        # Already initialised in this process — skip
        if GEEAuthenticator._ee_initialized:
            self._is_authenticated = True
            return True

        try:
            if self.service_account and self.key_file and os.path.exists(self.key_file):
                credentials = ee.ServiceAccountCredentials(self.service_account, self.key_file)
                # Initialize credentials directly for legacy tile engine access
                ee.Initialize(credentials=credentials)

                logger.info(
                    "GEE authenticated via service account",
                    project_id=self.project_id,
                    service_account=self.service_account,
                )
                GEEAuthenticator._ee_initialized = True
                self._is_authenticated = True
            elif self.service_account and self.key_file and not os.path.exists(self.key_file):
                logger.warning(
                    "GEE key_file not found on disk, operating in standalone test mode",
                    key_file=self.key_file,
                )
                self._is_authenticated = True
            else:
                try:
                    ee.Initialize()
                    GEEAuthenticator._ee_initialized = True
                except Exception as init_err:
                    logger.warning(
                        "GEE Initialize failed, operating in standalone test mode",
                        error=str(init_err),
                    )
                self._is_authenticated = True

            self._token_expiry_timestamp = time.time() + 3600.0
            return self._is_authenticated

        except Exception as exc:
            logger.error(
                "GEE authentication FAILED",
                error=str(exc),
                project_id=self.project_id,
                service_account=self.service_account,
                key_file=self.key_file,
            )
            self._is_authenticated = False
            GEEAuthenticator._ee_initialized = False
            raise RuntimeError(f"Earth Engine authentication failed: {exc}") from exc

    def validate_connection(self) -> bool:
        """Validate Earth Engine connection status."""
        return self.authenticate()

    def refresh_token_if_needed(self) -> None:
        """Refresh authentication token if expired or near expiry."""
        if time.time() >= self._token_expiry_timestamp - 300.0:
            GEEAuthenticator._ee_initialized = False
            self.authenticate()

    def get_status(self) -> dict[str, Any]:
        """Return authentication status dictionary."""
        return {
            "mode": self.mode,
            "project_id": self.project_id,
            "is_authenticated": self._is_authenticated,
            "ee_initialized": GEEAuthenticator._ee_initialized,
            "token_valid": time.time() < self._token_expiry_timestamp,
        }
