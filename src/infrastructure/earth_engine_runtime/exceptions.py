"""Custom Earth Engine domain exceptions for authentication, ROI validation, and tile generation."""

from src.shared.exceptions.base import DomainException, InfrastructureException


class AuthenticationError(InfrastructureException):
    """Exception raised when GEE authentication or authorization fails."""

    pass


class TileGenerationError(InfrastructureException):
    """Exception raised when map tile ID or URL generation fails."""

    pass


class InvalidROIError(DomainException):
    """Exception raised when an ROI polygon or bounding box is malformed or invalid."""

    pass


class DatasetUnavailableError(DomainException):
    """Exception raised when a requested satellite dataset or collection is unavailable."""

    pass


__all__ = [
    "AuthenticationError",
    "DatasetUnavailableError",
    "InvalidROIError",
    "TileGenerationError",
]
