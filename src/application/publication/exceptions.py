"""Typed publication engine exceptions."""


class PublicationError(Exception):
    """Base exception for all publication engine operations."""

    pass


class ReportValidationError(PublicationError):
    """Raised when scientific report quality validation fails."""

    pass


class RenderingError(PublicationError):
    """Raised when document rendering (Markdown, HTML, PDF, DOCX) fails."""

    pass


class CitationError(PublicationError):
    """Raised when citation formatting or traceability validation fails."""

    pass


class ExportError(PublicationError):
    """Raised when report export or file writing fails."""

    pass
