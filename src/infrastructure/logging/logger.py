"""Structured logging factory and formatters with workflow context correlation."""

import json
from typing import Any


class JSONFormatter:
    """Formatter outputting JSON structured log records."""

    @staticmethod
    def format(level: str, message: str, context: dict[str, Any] | None = None) -> str:
        """Format log entry as JSON string."""
        record = {
            "level": level.upper(),
            "message": message,
            "context": context or {},
        }
        return json.dumps(record)


class ConsoleFormatter:
    """Formatter outputting human-readable console log strings."""

    @staticmethod
    def format(level: str, message: str, context: dict[str, Any] | None = None) -> str:
        """Format log entry as console string."""
        ctx_str = f" | context={context}" if context else ""
        return f"[{level.upper()}] {message}{ctx_str}"


class StructuredLogger:
    """Logger recording structured entries with contextual metadata."""

    def __init__(self, name: str, json_format: bool = True) -> None:
        self.name = name
        self.json_format = json_format
        self._history: list[str] = []

    def log(self, level: str, message: str, context: dict[str, Any] | None = None) -> str:
        """Record log entry."""
        if self.json_format:
            output = JSONFormatter.format(level, message, context)
        else:
            output = ConsoleFormatter.format(level, message, context)
        self._history.append(output)
        return output

    def info(self, message: str, **kwargs: Any) -> str:
        """Log INFO entry."""
        return self.log("info", message, kwargs)

    def error(self, message: str, **kwargs: Any) -> str:
        """Log ERROR entry."""
        return self.log("error", message, kwargs)

    @property
    def history(self) -> list[str]:
        """Return recorded log lines history."""
        return list(self._history)


class WorkflowContextLogger:
    """Logger correlation wrapper attaching workflow_id and project_id metadata."""

    def __init__(self, logger: StructuredLogger, workflow_id: str, project_id: str) -> None:
        self.logger = logger
        self.workflow_id = workflow_id
        self.project_id = project_id

    def info(self, message: str, **kwargs: Any) -> str:
        """Log INFO entry with workflow correlation context."""
        ctx = {"workflow_id": self.workflow_id, "project_id": self.project_id, **kwargs}
        return self.logger.info(message, **ctx)


class LoggerFactory:
    """Factory creating structured loggers."""

    @staticmethod
    def get_logger(name: str, json_format: bool = True) -> StructuredLogger:
        """Factory method resolving structured logger instance."""
        return StructuredLogger(name, json_format=json_format)
