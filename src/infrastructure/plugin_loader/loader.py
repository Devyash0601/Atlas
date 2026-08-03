"""Dynamic plugin loader, metadata reader, and discovery integration."""

from dataclasses import dataclass
from typing import Any

from src.plugins.plugin import Plugin
from src.plugins.registry import registry


@dataclass(frozen=True)
class PluginMetadata:
    """Plugin metadata specification."""

    name: str
    version: str
    kind: str
    description: str


class PluginMetadataReader:
    """Metadata extractor for registered plugin instances."""

    @staticmethod
    def read(plugin: Plugin) -> PluginMetadata:
        """Extract metadata from plugin instance."""
        meta = plugin.metadata
        return PluginMetadata(
            name=meta.name,
            version=meta.version,
            kind=meta.kind.value,
            description=meta.description,
        )


class PluginDiscovery:
    """Discovery helper listing available registered plugins."""

    @staticmethod
    def discover_all() -> list[dict[str, Any]]:
        """List all plugins currently registered in PluginRegistry."""
        return registry.list_metadata()


class PluginLoader:
    """Dynamic plugin loader and integration manager."""

    def __init__(self) -> None:
        self._registry = registry

    def register(self, plugin: Plugin) -> None:
        """Register a plugin into registry."""
        self._registry.register(plugin)

    def load_plugin(self, name: str) -> Plugin | None:
        """Load registered plugin by name."""
        try:
            return self._registry.get_plugin(name)
        except Exception:
            return None
