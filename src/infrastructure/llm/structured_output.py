"""Pydantic-free production structured output parser with schema validation and type coercion."""

import json
from typing import Any

from src.infrastructure.llm.exceptions import StructuredOutputError


class StructuredOutputParser:
    """Production Pydantic-free JSON parser and validator."""

    @staticmethod
    def _clean_json_text(raw_text: str) -> str:
        """Strip markdown fences from raw LLM output text."""
        cleaned = raw_text.strip()
        if "```json" in cleaned:
            return cleaned.split("```json")[1].split("```")[0].strip()
        if "```" in cleaned:
            return cleaned.split("```")[1].split("```")[0].strip()
        return cleaned

    @classmethod
    def parse_json(cls, raw_text: str) -> dict[str, Any]:
        """Extract and parse JSON block without strict schema requirements."""
        return cls.parse_and_validate(raw_text, {})

    @classmethod
    def parse_and_validate(cls, raw_text: str, expected_schema: dict[str, Any]) -> dict[str, Any]:
        """Extract JSON block, validate against expected schema, and coerce types."""
        cleaned = cls._clean_json_text(raw_text)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise StructuredOutputError(f"Failed to decode LLM response as JSON: {err}") from err

        if not isinstance(parsed, dict):
            raise StructuredOutputError("Parsed JSON root must be a dictionary object.")

        required_fields = expected_schema.get("required", [])
        for req in required_fields:
            if req not in parsed:
                raise StructuredOutputError(f"Missing required JSON property '{req}'.")

        properties = expected_schema.get("properties", {})
        cls._coerce_properties(parsed, properties)
        return parsed

    @staticmethod
    def _coerce_properties(parsed: dict[str, Any], properties: dict[str, Any]) -> None:
        """Coerce dictionary properties according to type specifications."""
        for prop_name, prop_spec in properties.items():
            if prop_name not in parsed:
                continue
            val = parsed[prop_name]
            expected_type = prop_spec.get("type")
            if expected_type == "string" and not isinstance(val, str):
                parsed[prop_name] = str(val)
            elif expected_type == "number" and not isinstance(val, (int, float)):
                try:
                    parsed[prop_name] = float(val)
                except (ValueError, TypeError) as err:
                    raise StructuredOutputError(
                        f"Property '{prop_name}' cannot be coerced to number."
                    ) from err
            elif expected_type == "array" and not isinstance(val, list):
                raise StructuredOutputError(f"Property '{prop_name}' must be a list/array.")
