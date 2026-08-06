"""Typed Earth Engine runtime exceptions."""


class EarthEngineError(Exception):
    """Base exception for all Earth Engine runtime operations."""

    pass


class EEAuthenticationError(EarthEngineError):
    """Raised when Earth Engine authentication fails."""

    pass


class EEDatasetUnavailable(EarthEngineError, KeyError):
    """Raised when requested satellite dataset is not available in catalog."""

    pass


class EEPlanValidationError(EarthEngineError, ValueError):
    """Raised when GEEPlanSpec validation fails."""

    pass


class EECompilationError(EarthEngineError):
    """Raised when GEEPlanSpec compilation into API call tree fails."""

    pass


class EEExecutionError(EarthEngineError):
    """Raised when GEE computation execution encounters runtime error."""

    pass


class EEExportError(EarthEngineError):
    """Raised when Earth Engine asset or file export fails."""

    pass


class EETimeoutError(EarthEngineError):
    """Raised when GEE task execution exceeds timeout limit."""

    pass


class EEQuotaExceeded(EarthEngineError):
    """Raised when Earth Engine compute or memory quota limit is exceeded."""

    pass


class EERetryLimitExceeded(EarthEngineError):
    """Raised when Earth Engine task retries exceed maximum limit."""

    pass
