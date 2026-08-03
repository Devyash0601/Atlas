"""Unit tests for Sprint 3 Production Research Workflow Engine Subsystem."""

import pytest

from src.application.workflows.research_engine.artifact_store import ArtifactStore
from src.application.workflows.research_engine.dependency_resolver import DependencyResolver
from src.application.workflows.research_engine.exceptions import (
    CycleDetectedError,
    DependencyUnsatisfiedError,
)
from src.application.workflows.research_engine.execution_history import ExecutionHistory
from src.application.workflows.research_engine.task_queue import TaskQueue
from src.application.workflows.research_engine.task_router import TaskRouter
from src.application.workflows.research_engine.workflow_checkpoint import (
    WorkflowCheckpointManager,
)
from src.application.workflows.research_engine.workflow_context import WorkflowContext
from src.application.workflows.research_engine.workflow_engine import WorkflowEngine
from src.application.workflows.research_engine.workflow_graph import WorkflowGraph
from src.application.workflows.research_engine.workflow_metrics import WorkflowMetrics
from src.application.workflows.research_engine.workflow_scheduler import WorkflowScheduler
from src.application.workflows.research_engine.workflow_state import WorkflowState


def test_workflow_graph_dag_and_cycle_detection() -> None:
    """Verify DAG topological sorting and cycle detection error handling."""
    graph = WorkflowGraph()
    n1 = graph.add_node("n1", "ResearchPlanningTask")
    n2 = graph.add_node("n2", "LiteratureRetrievalTask", dependencies=[n1.node_id])
    graph.add_node("n3", "EvidenceCollectionTask", dependencies=[n2.node_id])

    order = graph.topological_sort()
    assert order == ["n1", "n2", "n3"]

    # Test cycle detection
    cycle_graph = WorkflowGraph()
    cycle_graph.add_node("c1", "Task1")
    cycle_graph.add_node("c2", "Task2", dependencies=["c1"])
    with pytest.raises(CycleDetectedError):
        cycle_graph.add_node("c1_cycle", "Task1", dependencies=["c2"])
        cycle_graph.edges["c2"].append("c1")
        cycle_graph.detect_cycles()


def test_workflow_scheduler_and_state() -> None:
    """Verify WorkflowScheduler ready nodes calculation and WorkflowState transitions."""
    graph = WorkflowGraph()
    n1 = graph.add_node("n1", "ResearchPlanningTask")
    graph.add_node("n2", "LiteratureRetrievalTask", dependencies=[n1.node_id])

    state = WorkflowState(workflow_id="wf_test", pending_nodes=["n1", "n2"])
    scheduler = WorkflowScheduler(graph)

    ready = scheduler.get_ready_nodes(state)
    assert ready == ["n1"]

    state.mark_running("n1")
    state.mark_completed("n1", duration_sec=1.5)

    ready_next = scheduler.get_ready_nodes(state)
    assert ready_next == ["n2"]


def test_artifact_store_and_dependency_resolver() -> None:
    """Verify immutable ArtifactStore versioning and DependencyResolver prerequisites."""
    graph = WorkflowGraph()
    graph.add_node(
        "n1",
        "ResearchPlanningTask",
        inputs={"required_artifact_type": "PlanArtifact"},
    )

    store = ArtifactStore()
    resolver = DependencyResolver(graph, store)
    state = WorkflowState(workflow_id="wf_test")

    with pytest.raises(DependencyUnsatisfiedError):
        resolver.verify_prerequisites("n1", state)

    store.store_artifact("PlanArtifact", "producer_0", {"plan": "NDVI analysis"})
    assert resolver.verify_prerequisites("n1", state) is True

    art1 = store.store_artifact("PlanArtifact", "producer_1", {"plan": "v2"})
    assert art1.version == 2
    assert store.get_latest_by_type("PlanArtifact").version == 2


def test_task_router_queue_and_history() -> None:
    """Verify TaskRouter task mapping, TaskQueue operations, and ExecutionHistory logging."""
    router = TaskRouter()
    subsystem = router.route_task("LiteratureRetrievalTask")
    assert subsystem == "Scientific RAG Subsystem"

    queue = TaskQueue()
    graph = WorkflowGraph()
    n1 = graph.add_node("n1", "Task1")
    queue.push(n1)
    assert queue.is_empty() is False
    assert queue.pop().node_id == "n1"
    assert queue.is_empty() is True

    history = ExecutionHistory()
    history.record_execution(
        record_id="rec1",
        node_id="n1",
        task_type="Task1",
        inputs={},
        outputs={"status": "OK"},
        duration_sec=0.5,
    )
    assert history.count() == 1
    assert history.get_history_for_node("n1")[0].status == "SUCCESS"


def test_checkpoint_manager_and_metrics() -> None:
    """Verify WorkflowCheckpointManager save/restore and WorkflowMetrics counters."""
    manager = WorkflowCheckpointManager()
    state = WorkflowState(workflow_id="wf_100", completed_nodes=["n1"])

    ckpt = manager.create_checkpoint(state)
    restored = manager.restore_checkpoint(ckpt.checkpoint_id)
    assert restored.workflow_id == "wf_100"
    assert restored.completed_nodes == ["n1"]

    metrics = WorkflowMetrics()
    metrics.record_llm_call()
    metrics.record_retrieval_call()
    history = ExecutionHistory()
    summary = metrics.compute_summary(state, history)
    assert summary["llm_calls_count"] == 1
    assert summary["retrieval_calls_count"] == 1


@pytest.mark.asyncio
async def test_workflow_engine_end_to_end_pipeline() -> None:
    """Verify WorkflowEngine building 7-stage DAG pipeline and executing end-to-end flow."""
    context = WorkflowContext(research_question="What is the LST impact on urban NDVI?")
    engine = WorkflowEngine(workflow_id="wf_e2e_1", context=context)
    engine.build_default_scientific_pipeline()

    assert len(engine.graph.nodes) == 7

    completed_state = await engine.run()
    assert completed_state.status == "COMPLETED"
    assert len(completed_state.completed_nodes) == 7
    assert len(engine.artifact_store.list_artifacts()) == 7
