"""WorkflowEngine main orchestration facade supporting workflow state management."""

from collections.abc import Callable
from typing import Any

from src.application.workflows.research_engine.artifact_store import ArtifactStore
from src.application.workflows.research_engine.exceptions import WorkflowError
from src.application.workflows.research_engine.workflow_checkpoint import WorkflowCheckpointManager
from src.application.workflows.research_engine.workflow_context import WorkflowContext
from src.application.workflows.research_engine.workflow_executor import WorkflowExecutor
from src.application.workflows.research_engine.workflow_graph import WorkflowGraph, WorkflowNode
from src.application.workflows.research_engine.workflow_metrics import WorkflowMetrics
from src.application.workflows.research_engine.workflow_scheduler import WorkflowScheduler
from src.application.workflows.research_engine.workflow_state import WorkflowState
from src.application.workflows.research_engine.workflow_validator import WorkflowValidator


class WorkflowEngine:
    """Main facade orchestrating autonomous research workflow execution."""

    def __init__(
        self,
        workflow_id: str = "wf_default",
        context: WorkflowContext | None = None,
        graph: WorkflowGraph | None = None,
    ) -> None:
        self.workflow_id = workflow_id
        self.context = context or WorkflowContext(
            research_question="Default Research Pipeline Question"
        )
        self.graph = graph or WorkflowGraph()
        self.artifact_store = ArtifactStore()
        self.state = WorkflowState(
            workflow_id=workflow_id,
            pending_nodes=list(self.graph.nodes.keys()),
        )
        self.scheduler = WorkflowScheduler(self.graph)
        self.executor = WorkflowExecutor(self.graph, self.artifact_store)
        self.checkpoint_manager = WorkflowCheckpointManager()
        self.validator = WorkflowValidator(self.graph, self.artifact_store)
        self.metrics = WorkflowMetrics()

    def build_default_scientific_pipeline(self) -> None:
        """Construct standard 7-stage research DAG pipeline."""
        n1 = self.graph.add_node("node_1_planner", "ResearchPlanningTask")
        n2 = self.graph.add_node(
            "node_2_lit_review",
            "LiteratureRetrievalTask",
            dependencies=[n1.node_id],
        )
        n3 = self.graph.add_node(
            "node_3_evidence",
            "EvidenceCollectionTask",
            dependencies=[n2.node_id],
        )
        n4 = self.graph.add_node(
            "node_4_verify",
            "VerificationTask",
            dependencies=[n3.node_id],
        )
        n5 = self.graph.add_node(
            "node_5_dataset",
            "DatasetPlanningTask",
            dependencies=[n4.node_id],
        )
        n6 = self.graph.add_node(
            "node_6_ee_plan",
            "EarthEnginePlanningTask",
            dependencies=[n5.node_id],
        )
        self.graph.add_node(
            "node_7_review",
            "WorkflowReviewTask",
            dependencies=[n6.node_id],
        )
        self.state.pending_nodes = list(self.graph.nodes.keys())

    async def run(
        self,
        custom_handler: Callable[[WorkflowNode], dict[str, Any]] | None = None,
    ) -> WorkflowState:
        """Execute workflow until completion or pause."""
        self.state.status = "RUNNING"

        while not self.scheduler.is_workflow_complete(self.state):
            if self.state.status in ["PAUSED", "CANCELLED"]:
                break

            ready_nodes = self.scheduler.get_ready_nodes(self.state)
            if not ready_nodes:
                if self.state.running_nodes:
                    continue
                # No ready nodes and none running -> stall or failure
                break

            for node_id in ready_nodes:
                try:
                    await self.executor.execute_node(
                        node_id, self.state, custom_handler=custom_handler
                    )
                except Exception as err:
                    if self.state.retry_counts.get(node_id, 0) >= 3:
                        self.state.status = "FAILED"
                        raise WorkflowError(f"Workflow failed at node '{node_id}': {err}") from err

        if self.scheduler.is_workflow_complete(self.state):
            self.state.status = "COMPLETED"
            self.validator.validate_workflow_integrity(self.state)

        return self.state

    def pause(self) -> None:
        """Pause running workflow."""
        if self.state.status == "RUNNING":
            self.state.status = "PAUSED"

    def resume(self) -> None:
        """Resume paused workflow."""
        if self.state.status == "PAUSED":
            self.state.status = "RUNNING"

    def cancel(self) -> None:
        """Cancel workflow execution."""
        self.state.status = "CANCELLED"

    def checkpoint(self) -> str:
        """Save workflow checkpoint and return checkpoint ID."""
        payload = self.checkpoint_manager.create_checkpoint(self.state)
        return payload.checkpoint_id

    def recover(self, checkpoint_id: str) -> WorkflowState:
        """Recover workflow state from checkpoint ID."""
        self.state = self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        return self.state
