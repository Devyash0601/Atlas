"""Database connection foundation, transaction manager, and migration manager interface."""

from abc import ABC, abstractmethod
from typing import Any


class DatabaseConnection:
    """Infrastructure database connection state holder."""

    def __init__(self, connection_url: str) -> None:
        self.connection_url = connection_url
        self.is_connected = False

    async def connect(self) -> None:
        """Establish database connection."""
        self.is_connected = True

    async def disconnect(self) -> None:
        """Close database connection."""
        self.is_connected = False


class ConnectionFactory:
    """Factory creating database connection instances."""

    @staticmethod
    def create_connection(connection_url: str) -> DatabaseConnection:
        """Create database connection instance."""
        return DatabaseConnection(connection_url)


class RepositoryFactory(ABC):
    """Abstract repository factory contract."""

    @abstractmethod
    def create_repository(self, repository_type: type) -> Any:
        """Instantiate repository implementation."""
        pass


class MigrationManager(ABC):
    """Abstract migration manager interface."""

    @abstractmethod
    async def run_migrations(self) -> None:
        """Execute database schema migrations."""
        pass


class TransactionManager(ABC):
    """Abstract database transaction manager interface."""

    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin transaction boundary."""
        pass

    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit transaction changes."""
        pass

    @abstractmethod
    async def rollback_transaction(self) -> None:
        """Roll back transaction changes."""
        pass
