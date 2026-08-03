"""Scientific verification status domain enum."""

from enum import StrEnum


class VerificationStatus(StrEnum):
    """Evidence verification classifications for scientific claims."""

    VERIFIED = "verified"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"
