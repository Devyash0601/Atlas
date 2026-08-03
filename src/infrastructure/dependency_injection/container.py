"""Lightweight Dependency Injection Container with singleton, transient, and scoped providers."""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class SingletonProvider[T]:
    """Provider returning a cached singleton instance."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._instance: T | None = None

    def get(self) -> T:
        """Resolve singleton instance."""
        if self._instance is None:
            self._instance = self._factory()
        return self._instance


class TransientProvider[T]:
    """Provider returning a fresh new instance on every resolution."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory

    def get(self) -> T:
        """Resolve fresh transient instance."""
        return self._factory()


class ScopedProvider[T]:
    """Provider returning an instance scoped to a context lifecycle."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._scoped_instance: T | None = None

    def get(self) -> T:
        """Resolve scoped instance."""
        if self._scoped_instance is None:
            self._scoped_instance = self._factory()
        return self._scoped_instance

    def reset(self) -> None:
        """Clear scoped instance."""
        self._scoped_instance = None


class Container:
    """Inversion of Control (IoC) Container supporting constructor injection."""

    def __init__(self) -> None:
        self._singletons: dict[type, Any] = {}
        self._transients: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}

    def register_singleton[T](self, service_type: type[T], instance: T) -> None:
        """Register a singleton instance for service type."""
        self._singletons[service_type] = instance

    def register_transient[T](self, service_type: type[T], factory: Callable[[], T]) -> None:
        """Register a transient factory for service type."""
        self._transients[service_type] = factory

    def resolve[T](self, service_type: type[T]) -> T:
        """Resolve instance for requested service type."""
        if service_type in self._singletons:
            return self._singletons[service_type]  # type: ignore[no-any-return]
        if service_type in self._transients:
            factory = self._transients[service_type]
            return factory()  # type: ignore[no-any-return]
        raise KeyError(f"Service '{service_type.__name__}' is not registered in DI Container.")


class ServiceRegistry:
    """Global service registry container singleton wrapper."""

    _container: Container | None = None

    @classmethod
    def get_container(cls) -> Container:
        """Get global IoC container instance."""
        if cls._container is None:
            cls._container = Container()
        return cls._container
