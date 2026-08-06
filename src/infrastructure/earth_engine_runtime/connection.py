"""Earth Engine connection abstractions and backward compatibility aliases."""

from src.infrastructure.earth_engine_runtime.gee_authenticator import GEEAuthenticator
from src.infrastructure.earth_engine_runtime.gee_client import GEEClient

# Backward compatibility alias
GEEConnectionManager = GEEClient

__all__ = ["GEEAuthenticator", "GEEClient", "GEEConnectionManager"]
