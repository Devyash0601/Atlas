"""Typed exceptions for Research Workflow Engine."""


class WorkflowError(Exception):
    """Base exception for all research workflow engine errors."""

    pass


class CycleDetectedError(WorkflowError):
    """Raised when DAG graph construction detects a cyclic dependency loop."""

    pass


class NodeExecutionError(WorkflowError):
    """Raised when execution of a workflow node fails."""

    pass


class DependencyUnsatisfiedError(WorkflowError):
    """Raised when required node dependencies or input artifacts are missing."""

    pass


class CheckpointError(WorkflowError):
    """Raised when workflow checkpoint save or restore operations fail."""

    pass


class ValidationError(WorkflowError):
    """Raised when workflow or artifact integrity validation fails."""

    pass
