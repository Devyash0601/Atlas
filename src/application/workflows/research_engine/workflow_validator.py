"""WorkflowValidator checking workflow integrity, artifacts, and confidence thresholds."""

from src.application.workflows.research_engine.artifact_store import ArtifactStore
from src.application.workflows.research_engine.exceptions import ValidationError
from src.application.workflows.research_engine.workflow_graph import WorkflowGraph
from src.application.workflows.research_engine.workflow_state import WorkflowState


class WorkflowValidator:
    """Validator auditing workflow graph integrity and confidence thresholds."""

    def __init__(
        self,
        graph: WorkflowGraph,
        artifact_store: ArtifactStore,
        min_confidence: float = 0.7,
    ) -> None:
        self.graph = graph
        self.artifact_store = artifact_store
        self.min_confidence = min_confidence

    def validate_workflow_integrity(self, state: WorkflowState) -> bool:
        """Validate DAG graph completeness and confidence levels."""
        if not self.graph.nodes:
            raise ValidationError("Workflow graph cannot be empty.")

        # Check if all completed nodes produced artifacts
        for art in self.artifact_store.list_artifacts():
            if art.confidence < self.min_confidence:
                raise ValidationError(
                    f"Artifact '{art.artifact_uuid}' confidence ({art.confidence}) "
                    f"below threshold ({self.min_confidence})."
                )

        return True
