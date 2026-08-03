"""WorkflowScheduler determining ready, parallel, and blocked tasks."""

from src.application.workflows.research_engine.workflow_graph import WorkflowGraph
from src.application.workflows.research_engine.workflow_state import WorkflowState


class WorkflowScheduler:
    """Scheduler assessing node dependencies and ready task execution sets."""

    def __init__(self, graph: WorkflowGraph) -> None:
        self.graph = graph

    def get_ready_nodes(self, state: WorkflowState) -> list[str]:
        """Return list of ready node IDs whose dependencies are satisfied."""
        ready: list[str] = []
        completed_set = set(state.completed_nodes)

        for node_id, node in self.graph.nodes.items():
            if node_id in completed_set or node_id in state.running_nodes:
                continue
            if node_id in state.failed_nodes and state.retry_counts.get(node_id, 0) >= 3:
                continue

            # Check if all parent dependencies are completed
            if all(dep in completed_set for dep in node.dependencies):
                ready.append(node_id)

        return ready

    def is_workflow_complete(self, state: WorkflowState) -> bool:
        """Return True when all nodes in graph are completed."""
        return len(state.completed_nodes) == len(self.graph.nodes)
