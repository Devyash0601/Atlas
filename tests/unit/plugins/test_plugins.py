"""Unit tests for ATLAS-EO Plugin Architecture Framework."""

from typing import Any

import pytest

from src.plugins import Plugin, PluginKind, PluginMetadata, PluginRegistry
from src.shared.exceptions.base import NotFoundException, ValidationException


class DummyLLMPlugin(Plugin):
    """Dummy test implementation of Plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dummy-llm",
            version="1.0.0",
            kind=PluginKind.LLM,
            description="Dummy LLM test plugin",
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass


def test_plugin_registration_and_retrieval() -> None:
    """Verify plugin registration, kind filtering, and error handling."""
    reg = PluginRegistry()
    plugin = DummyLLMPlugin()

    reg.register(plugin)
    assert reg.get_plugin("dummy-llm") == plugin

    llm_plugins = reg.get_plugins_by_kind(PluginKind.LLM)
    assert len(llm_plugins) == 1
    assert llm_plugins[0] == plugin

    # Test duplicate registration error
    with pytest.raises(ValidationException):
        reg.register(plugin)

    # Test unregistration
    reg.unregister("dummy-llm")
    with pytest.raises(NotFoundException):
        reg.get_plugin("dummy-llm")
