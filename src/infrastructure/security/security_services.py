"""Security service abstract contracts."""

from abc import ABC, abstractmethod
from typing import Any


class SecretManager(ABC):
    """Abstract secret manager interface contract."""

    @abstractmethod
    async def get_secret(self, secret_name: str) -> str:
        """Fetch secret string by name."""
        pass


class TokenProvider(ABC):
    """Abstract token provider interface contract."""

    @abstractmethod
    async def create_token(self, payload: dict[str, Any]) -> str:
        """Create token string from payload."""
        pass

    @abstractmethod
    async def decode_token(self, token: str) -> dict[str, Any]:
        """Decode token payload."""
        pass


class EncryptionService(ABC):
    """Abstract encryption service contract."""

    @abstractmethod
    async def encrypt(self, plain_text: str) -> str:
        """Encrypt plain text to cipher text."""
        pass

    @abstractmethod
    async def decrypt(self, cipher_text: str) -> str:
        """Decrypt cipher text to plain text."""
        pass


class HashingService(ABC):
    """Abstract hashing service contract."""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash plain text password."""
        pass

    @abstractmethod
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify plain text password against hash."""
        pass
