"""Thread-safe Plugin Registry for managing active extension plugins."""

import threading
from typing import Any

from src.plugins.plugin import Plugin, PluginKind, PluginMetadata
from src.shared.exceptions.base import NotFoundException, ValidationException
from src.shared.logging.logger import get_logger

logger = get_logger(__name__)


class PluginRegistry:
    """Central thread-safe registry for ATLAS-EO plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._by_kind: dict[PluginKind, list[Plugin]] = {kind: [] for kind in PluginKind}
        self._lock = threading.Lock()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance into the central registry."""
        meta: PluginMetadata = plugin.metadata
        with self._lock:
            if meta.name in self._plugins:
                raise ValidationException(f"Plugin '{meta.name}' is already registered.")

            self._plugins[meta.name] = plugin
            self._by_kind[meta.kind].append(plugin)
            logger.info("Registered plugin", plugin_name=meta.name, kind=meta.kind)

    def unregister(self, plugin_name: str) -> None:
        """Remove a plugin from the registry by name."""
        with self._lock:
            if plugin_name not in self._plugins:
                raise NotFoundException(f"Plugin '{plugin_name}' not found.")

            plugin = self._plugins.pop(plugin_name)
            self._by_kind[plugin.metadata.kind].remove(plugin)
            logger.info("Unregistered plugin", plugin_name=plugin_name)

    def get_plugin(self, name: str) -> Plugin:
        """Retrieve a registered plugin by unique name."""
        with self._lock:
            if name not in self._plugins:
                raise NotFoundException(f"Plugin '{name}' not found.")
            return self._plugins[name]

    def get_plugins_by_kind(self, kind: PluginKind) -> list[Plugin]:
        """Retrieve all registered plugins of a specific category type."""
        with self._lock:
            return list(self._by_kind.get(kind, []))

    def list_metadata(self) -> list[dict[str, Any]]:
        """Return a list of metadata dictionaries for all active plugins."""
        with self._lock:
            return [p.metadata.model_dump() for p in self._plugins.values()]


# Global singleton plugin registry instance
registry = PluginRegistry()
