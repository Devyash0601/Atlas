"""DependencyResolver verifying node dependencies and required artifacts."""

from src.application.workflows.research_engine.artifact_store import ArtifactStore
from src.application.workflows.research_engine.exceptions import DependencyUnsatisfiedError
from src.application.workflows.research_engine.workflow_graph import WorkflowGraph
from src.application.workflows.research_engine.workflow_state import WorkflowState


class DependencyResolver:
    """Resolver validating node input prerequisites before execution."""

    def __init__(self, graph: WorkflowGraph, artifact_store: ArtifactStore) -> None:
        self.graph = graph
        self.artifact_store = artifact_store

    def verify_prerequisites(self, node_id: str, state: WorkflowState) -> bool:
        """Verify node dependencies and required artifact inputs."""
        node = self.graph.nodes.get(node_id)
        if not node:
            raise DependencyUnsatisfiedError(f"Node '{node_id}' does not exist in graph.")

        for parent_id in node.dependencies:
            if parent_id not in state.completed_nodes:
                raise DependencyUnsatisfiedError(
                    f"Parent node '{parent_id}' must complete before node '{node_id}' can run."
                )

        required_artifact_type = node.inputs.get("required_artifact_type")
        if required_artifact_type:
            art = self.artifact_store.get_latest_by_type(required_artifact_type)
            if not art:
                raise DependencyUnsatisfiedError(
                    f"Node '{node_id}' requires missing artifact type '{required_artifact_type}'."
                )

        return True
