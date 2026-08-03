"""Unit tests for Structured Logging, EventBus, and PluginLoader integration."""

from typing import Any

from src.application.events.application_events import ApplicationEvent
from src.domain.base.domain_event import DomainEvent
from src.infrastructure.events.event_bus import (
    ApplicationEventDispatcher,
    DomainEventDispatcher,
    EventBus,
)
from src.infrastructure.logging.logger import LoggerFactory, StructuredLogger, WorkflowContextLogger
from src.infrastructure.plugin_loader.loader import (
    PluginDiscovery,
    PluginLoader,
    PluginMetadataReader,
)
from src.plugins.plugin import Plugin, PluginKind, PluginMetadata


def test_structured_logger_json_and_console() -> None:
    """Verify StructuredLogger formatting."""
    json_logger = LoggerFactory.get_logger("test_json", json_format=True)
    out1 = json_logger.info("Test message", key="val")
    assert '"level": "INFO"' in out1
    assert '"key": "val"' in out1

    console_logger = StructuredLogger("test_console", json_format=False)
    out2 = console_logger.error("Error occurred", code=500)
    assert "[ERROR]" in out2
    assert "code" in out2
    assert "500" in out2

    wf_logger = WorkflowContextLogger(json_logger, workflow_id="wf_123", project_id="p_456")
    out3 = wf_logger.info("Workflow step started")
    assert '"workflow_id": "wf_123"' in out3
    assert len(json_logger.history) == 2


def test_event_bus_and_dispatchers() -> None:
    """Verify EventBus publish/subscribe and event dispatchers."""
    bus = EventBus()
    received_events: list[Any] = []

    class CustomEvent(DomainEvent):
        pass

    bus.subscribe(CustomEvent, lambda e: received_events.append(e))

    domain_dispatcher = DomainEventDispatcher(bus)
    evt = CustomEvent()
    domain_dispatcher.dispatch(evt)

    assert len(received_events) == 1
    assert received_events[0] is evt

    app_events: list[ApplicationEvent] = []

    class CustomAppEvent(ApplicationEvent):
        pass

    bus.subscribe(CustomAppEvent, lambda e: app_events.append(e))
    app_dispatcher = ApplicationEventDispatcher(bus)
    app_evt = CustomAppEvent()
    app_dispatcher.dispatch(app_evt)

    assert len(app_events) == 1
    assert app_events[0] is app_evt


class DummyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_infra_plugin",
            version="1.0.0",
            kind=PluginKind.LLM,
            description="Dummy test plugin",
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass


def test_plugin_loader_integration() -> None:
    """Verify PluginLoader, PluginMetadataReader, and PluginDiscovery."""
    loader = PluginLoader()
    plugin = DummyPlugin()
    loader.register(plugin)

    loaded = loader.load_plugin("test_infra_plugin")
    assert loaded is plugin
    assert loader.load_plugin("non_existent") is None

    meta = PluginMetadataReader.read(plugin)
    assert meta.name == "test_infra_plugin"
    assert meta.kind == "llm"

    plugins_list = PluginDiscovery.discover_all()
    assert any(p["name"] == "test_infra_plugin" for p in plugins_list)
