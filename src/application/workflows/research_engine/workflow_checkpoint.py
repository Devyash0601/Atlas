"""WorkflowCheckpointManager saving, restoring, and recovering state checkpoints."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.application.workflows.research_engine.exceptions import CheckpointError
from src.application.workflows.research_engine.workflow_state import WorkflowState


@dataclass
class WorkflowCheckpointPayload:
    """Serializable checkpoint payload snapshot."""

    checkpoint_id: str
    workflow_id: str
    state_data: dict[str, Any]
    timestamp: str


class WorkflowCheckpointManager:
    """Manager supporting save, restore, and crash recovery checkpoints."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, WorkflowCheckpointPayload] = {}

    def create_checkpoint(self, state: WorkflowState) -> WorkflowCheckpointPayload:
        """Create and store snapshot checkpoint payload."""
        ckpt_id = f"ckpt_{state.workflow_id}_{len(self._checkpoints) + 1}"
        payload = WorkflowCheckpointPayload(
            checkpoint_id=ckpt_id,
            workflow_id=state.workflow_id,
            state_data=state.to_dict(),
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._checkpoints[ckpt_id] = payload
        return payload

    def restore_checkpoint(self, checkpoint_id: str) -> WorkflowState:
        """Restore WorkflowState from checkpoint ID."""
        if checkpoint_id not in self._checkpoints:
            raise CheckpointError(f"Checkpoint ID '{checkpoint_id}' not found.")

        data = self._checkpoints[checkpoint_id].state_data
        state = WorkflowState(
            workflow_id=data["workflow_id"],
            status=data["status"],
            current_node=data["current_node"],
            completed_nodes=data["completed_nodes"],
            failed_nodes=data["failed_nodes"],
            pending_nodes=data["pending_nodes"],
            running_nodes=data["running_nodes"],
            retry_counts=data["retry_counts"],
            node_timings=data["node_timings"],
            overall_confidence=data["overall_confidence"],
            produced_artifact_uuids=data["produced_artifact_uuids"],
        )
        return state

    def serialize_checkpoint(self, checkpoint_id: str) -> str:
        """Serialize checkpoint payload to JSON string."""
        if checkpoint_id not in self._checkpoints:
            raise CheckpointError(f"Checkpoint ID '{checkpoint_id}' not found.")
        payload = self._checkpoints[checkpoint_id]
        return json.dumps(
            {
                "checkpoint_id": payload.checkpoint_id,
                "workflow_id": payload.workflow_id,
                "state_data": payload.state_data,
                "timestamp": payload.timestamp,
            }
        )
