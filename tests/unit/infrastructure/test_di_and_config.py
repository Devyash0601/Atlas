"""Unit tests for Dependency Injection Container and Configuration Settings."""

import pytest

from src.infrastructure.config.settings import (
    ConfigurationLoader,
    DevelopmentSettings,
    ProductionSettings,
    TestingSettings,
)
from src.infrastructure.dependency_injection.container import (
    Container,
    ScopedProvider,
    ServiceRegistry,
    SingletonProvider,
    TransientProvider,
)


def test_configuration_loader() -> None:
    """Verify ConfigurationLoader instantiates typed Settings subclasses."""
    dev = ConfigurationLoader.load("development")
    assert isinstance(dev, DevelopmentSettings)
    assert dev.environment == "development"
    assert dev.debug is True

    test_s = ConfigurationLoader.load("testing")
    assert isinstance(test_s, TestingSettings)
    assert test_s.environment == "testing"

    prod = ConfigurationLoader.load("production")
    assert isinstance(prod, ProductionSettings)
    assert prod.environment == "production"
    assert prod.debug is False


class DummyService:
    def __init__(self, value: int = 42) -> None:
        self.value = value


def test_di_container_singleton_and_transient() -> None:
    """Verify Container singleton and transient resolution."""
    container = Container()
    dummy = DummyService(100)

    # Singleton registration
    container.register_singleton(DummyService, dummy)
    resolved = container.resolve(DummyService)
    assert resolved is dummy

    # Transient registration
    container2 = Container()
    container2.register_transient(DummyService, lambda: DummyService(200))
    r1 = container2.resolve(DummyService)
    r2 = container2.resolve(DummyService)
    assert r1 is not r2
    assert r1.value == 200

    # Unregistered key error
    class Unregistered:
        pass

    with pytest.raises(KeyError):
        container.resolve(Unregistered)


def test_di_providers_and_service_registry() -> None:
    """Verify SingletonProvider, TransientProvider, ScopedProvider, and ServiceRegistry."""
    sp = SingletonProvider(lambda: DummyService(1))
    assert sp.get() is sp.get()

    tp = TransientProvider(lambda: DummyService(2))
    assert tp.get() is not tp.get()

    scp = ScopedProvider(lambda: DummyService(3))
    inst1 = scp.get()
    assert scp.get() is inst1
    scp.reset()
    assert scp.get() is not inst1

    reg = ServiceRegistry.get_container()
    assert isinstance(reg, Container)
