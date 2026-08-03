"""High-level application services for domain boundaries."""

from typing import Any

from src.application.exceptions.application_exceptions import QueryFailed
from src.application.transactions.unit_of_work import UnitOfWork
from src.application.workflows.workflow_coordinator import WorkflowCoordinator


class ProjectApplicationService:
    """Application service orchestrating research projects."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._coordinator = WorkflowCoordinator(uow)

    @property
    def coordinator(self) -> WorkflowCoordinator:
        """Return workflow coordinator instance."""
        return self._coordinator


class WorkflowApplicationService:
    """Application service orchestrating workflows."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_workflow_dto(self, workflow_id: str) -> dict[str, Any]:
        """Query workflow state by ID."""
        import uuid

        try:
            wf_uuid = uuid.UUID(workflow_id)
        except ValueError as err:
            raise QueryFailed(f"Invalid workflow_id UUID: {workflow_id}") from err

        async with self._uow as uow:
            wf = await uow.workflows.find_by_id(wf_uuid)
            if not wf:
                raise QueryFailed(f"Workflow '{workflow_id}' not found.")
            return {
                "id": str(wf.id),
                "project_id": str(wf.project_id),
                "status": wf.status.value,
            }
