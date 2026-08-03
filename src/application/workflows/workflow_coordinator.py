"""WorkflowCoordinator managing use cases, transaction boundaries, and event notifications."""

from src.application.commands.evidence_commands import AddEvidenceCommand, VerifyEvidenceCommand
from src.application.commands.project_commands import (
    ApproveWorkflowCommand,
    CreateProjectCommand,
    CreateWorkflowCommand,
    ExecuteWorkflowCommand,
)
from src.application.dto.evidence_dto import EvidenceDTO
from src.application.dto.project_dto import ProjectDTO
from src.application.dto.verification_dto import VerificationDTO
from src.application.dto.workflow_dto import WorkflowDTO
from src.application.events.application_events import (
    ApplicationEvent,
    EvidenceVerified,
    ProjectStarted,
    WorkflowApproved,
    WorkflowCompleted,
)
from src.application.handlers.command_handlers import (
    AddEvidenceHandler,
    ApproveWorkflowHandler,
    CreateProjectHandler,
    CreateWorkflowHandler,
    ExecuteWorkflowHandler,
    VerifyEvidenceHandler,
)
from src.application.transactions.unit_of_work import UnitOfWork


class WorkflowCoordinator:
    """Central use case orchestrator handling transaction boundaries and event notifications."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._event_subscribers: list[ApplicationEvent] = []

    def dispatch_event(self, event: ApplicationEvent) -> None:
        """Record and dispatch an application event."""
        self._event_subscribers.append(event)

    def get_dispatched_events(self) -> list[ApplicationEvent]:
        """Retrieve dispatched application events."""
        return list(self._event_subscribers)

    async def create_project(self, cmd: CreateProjectCommand) -> ProjectDTO:
        """Execute project creation use case."""
        handler = CreateProjectHandler(self._uow)
        project_dto = await handler.handle(cmd)
        self.dispatch_event(ProjectStarted(project_id=project_dto.id))
        return project_dto

    async def create_workflow(self, cmd: CreateWorkflowCommand) -> WorkflowDTO:
        """Execute workflow planning use case."""
        handler = CreateWorkflowHandler(self._uow)
        return await handler.handle(cmd)

    async def approve_workflow(self, cmd: ApproveWorkflowCommand) -> WorkflowDTO:
        """Execute workflow approval use case."""
        handler = ApproveWorkflowHandler(self._uow)
        workflow_dto = await handler.handle(cmd)
        event = WorkflowApproved(
            workflow_id=workflow_dto.id,
            approver_user_id=cmd.approver_user_id,
        )
        self.dispatch_event(event)
        return workflow_dto

    async def execute_workflow(self, cmd: ExecuteWorkflowCommand) -> WorkflowDTO:
        """Execute workflow execution use case."""
        handler = ExecuteWorkflowHandler(self._uow)
        workflow_dto = await handler.handle(cmd)
        self.dispatch_event(WorkflowCompleted(workflow_id=workflow_dto.id))
        return workflow_dto

    async def add_evidence(self, cmd: AddEvidenceCommand) -> EvidenceDTO:
        """Execute evidence collection use case."""
        handler = AddEvidenceHandler(self._uow)
        return await handler.handle(cmd)

    async def verify_evidence(self, cmd: VerifyEvidenceCommand) -> VerificationDTO:
        """Execute verification use case."""
        handler = VerifyEvidenceHandler(self._uow)
        verification_dto = await handler.handle(cmd)
        self.dispatch_event(
            EvidenceVerified(
                verification_id=verification_dto.id,
                workflow_id=verification_dto.workflow_id,
                status=verification_dto.status,
            )
        )
        return verification_dto
