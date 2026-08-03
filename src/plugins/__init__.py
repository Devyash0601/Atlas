"""Plugin architecture framework for ATLAS-EO extensions."""

from src.plugins.loader import (
    EarthEnginePluginContract,
    EmbeddingPluginContract,
    LLMPluginContract,
    PluginLoader,
    StoragePluginContract,
    VisionPluginContract,
)
from src.plugins.plugin import Plugin, PluginKind, PluginMetadata
from src.plugins.registry import PluginRegistry, registry

__all__ = [
    "EarthEnginePluginContract",
    "EmbeddingPluginContract",
    "LLMPluginContract",
    "Plugin",
    "PluginKind",
    "PluginLoader",
    "PluginMetadata",
    "PluginRegistry",
    "StoragePluginContract",
    "VisionPluginContract",
    "registry",
]
