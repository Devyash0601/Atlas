"""Serialization utilities for JSON, YAML, binary, entities, and DTOs."""

import json
from typing import Any

from src.domain.base.entity import Entity


class JsonSerializer:
    """JSON serializer and deserializer."""

    @staticmethod
    def serialize(data: Any) -> str:
        """Serialize python object to JSON string."""
        return json.dumps(data, default=str)

    @staticmethod
    def deserialize(json_str: str) -> Any:
        """Deserialize JSON string to python dictionary or object."""
        return json.loads(json_str)


class YamlSerializer:
    """Dummy YAML serializer fallback."""

    @staticmethod
    def serialize(data: dict[str, Any]) -> str:
        """Serialize data to formatted YAML string structure."""
        lines = [f"{k}: {v}" for k, v in data.items()]
        return "\n".join(lines)


class BinarySerializer:
    """Binary serializer converting strings/utf-8 to bytes."""

    @staticmethod
    def serialize(text: str) -> bytes:
        """Encode text to UTF-8 bytes."""
        return text.encode("utf-8")

    @staticmethod
    def deserialize(data: bytes) -> str:
        """Decode UTF-8 bytes to text."""
        return data.decode("utf-8")


class EntitySerializer:
    """Entity serializer converting domain entities to state dictionary."""

    @staticmethod
    def serialize(entity: Entity) -> dict[str, Any]:
        """Convert entity properties to dictionary representation."""
        return {
            "id": str(entity.id),
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
        }


class DTOSerializer:
    """DTO serializer converting application dataclass DTOs to JSON."""

    @staticmethod
    def serialize(dto: Any) -> str:
        """Convert DTO dataclass to JSON string."""
        if hasattr(dto, "__dict__"):
            return json.dumps(dto.__dict__, default=str)
        return json.dumps(dto, default=str)
