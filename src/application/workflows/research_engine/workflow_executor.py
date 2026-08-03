"""WorkflowExecutor executing nodes asynchronously with retries and structured output."""

import time
from collections.abc import Callable
from typing import Any

from src.application.workflows.research_engine.artifact_store import ArtifactStore
from src.application.workflows.research_engine.dependency_resolver import DependencyResolver
from src.application.workflows.research_engine.exceptions import NodeExecutionError
from src.application.workflows.research_engine.execution_history import ExecutionHistory
from src.application.workflows.research_engine.task_router import TaskRouter
from src.application.workflows.research_engine.workflow_graph import (
    WorkflowGraph,
    WorkflowNode,
)
from src.application.workflows.research_engine.workflow_state import WorkflowState


class WorkflowExecutor:
    """Async executor running workflow graph nodes with retries and validation."""

    def __init__(
        self,
        graph: WorkflowGraph,
        artifact_store: ArtifactStore,
        task_router: TaskRouter | None = None,
    ) -> None:
        self.graph = graph
        self.artifact_store = artifact_store
        self.dependency_resolver = DependencyResolver(graph, artifact_store)
        self.task_router = task_router or TaskRouter()
        self.execution_history = ExecutionHistory()

    async def execute_node(
        self,
        node_id: str,
        state: WorkflowState,
        custom_handler: Callable[[WorkflowNode], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Execute single graph node asynchronously with dependency verification."""
        self.dependency_resolver.verify_prerequisites(node_id, state)
        node = self.graph.nodes[node_id]

        state.mark_running(node_id)
        start_time = time.time()
        attempt = state.retry_counts.get(node_id, 0) + 1

        try:
            if custom_handler:
                outputs = custom_handler(node)
            else:
                outputs = self.task_router.execute_routed_task(node.task_type, node.inputs)

            duration = round(time.time() - start_time, 3)
            state.mark_completed(node_id, duration)

            # Store produced artifact
            art = self.artifact_store.store_artifact(
                artifact_type=f"{node.task_type}_Artifact",
                producer_node_id=node_id,
                content=outputs,
                confidence=outputs.get("confidence", 1.0),
            )
            state.produced_artifact_uuids.append(art.artifact_uuid)

            self.execution_history.record_execution(
                record_id=f"exec_{node_id}_{attempt}",
                node_id=node_id,
                task_type=node.task_type,
                inputs=node.inputs,
                outputs=outputs,
                duration_sec=duration,
                status="SUCCESS",
                retry_count=attempt - 1,
            )
            return outputs

        except Exception as err:
            duration = round(time.time() - start_time, 3)
            state.mark_failed(node_id)
            self.execution_history.record_execution(
                record_id=f"exec_{node_id}_{attempt}",
                node_id=node_id,
                task_type=node.task_type,
                inputs=node.inputs,
                outputs={},
                duration_sec=duration,
                status="FAILED",
                error_message=str(err),
                retry_count=attempt - 1,
            )
            raise NodeExecutionError(f"Node '{node_id}' failed: {err}") from err
