"""Single-responsibility command handlers coordinating UnitOfWork, Entities, and Events."""

import uuid

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
from src.application.exceptions.application_exceptions import CommandFailed
from src.application.mappers.entity_dto_mapper import EntityDTOMapper
from src.application.transactions.unit_of_work import UnitOfWork
from src.application.validators.command_validators import CommandValidator
from src.domain.entities.evidence import Evidence
from src.domain.entities.research_project import ResearchProject
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow
from src.domain.enums.verification_status import VerificationStatus
from src.domain.value_objects.confidence_score import ConfidenceScore
from src.domain.value_objects.coordinate import Coordinate
from src.domain.value_objects.geo_bounds import GeoBounds
from src.domain.value_objects.region_of_interest import RegionOfInterest
from src.domain.value_objects.research_question import ResearchQuestion


class CreateProjectHandler:
    """Handler for CreateProjectCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: CreateProjectCommand) -> ProjectDTO:
        """Validate input command, create ResearchProject aggregate root, and persist."""
        CommandValidator.validate_create_project(cmd)

        sw = Coordinate(latitude=cmd.south_west_lat, longitude=cmd.south_west_lon)
        ne = Coordinate(latitude=cmd.north_east_lat, longitude=cmd.north_east_lon)
        bounds = GeoBounds(south_west=sw, north_east=ne)
        roi = RegionOfInterest(name=cmd.region_name, bounds=bounds)
        question = ResearchQuestion(text=cmd.question_text)
        user_id = uuid.UUID(cmd.user_id)

        project = ResearchProject(
            title=cmd.title,
            question=question,
            roi=roi,
            user_id=user_id,
        )

        async with self._uow as uow:
            await uow.projects.save(project)

        return EntityDTOMapper.project_to_dto(project)


class CreateWorkflowHandler:
    """Handler for CreateWorkflowCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: CreateWorkflowCommand) -> WorkflowDTO:
        """Validate input command and create Workflow entity."""
        CommandValidator.validate_create_workflow(cmd)
        project_id = uuid.UUID(cmd.project_id)

        async with self._uow as uow:
            project = await uow.projects.find_by_id(project_id)
            if not project:
                raise CommandFailed(f"Parent research project '{cmd.project_id}' not found.")

            workflow = Workflow(
                project_id=project_id,
                planner_output=cmd.planner_output,
            )
            await uow.workflows.save(workflow)

        return EntityDTOMapper.workflow_to_dto(workflow)


class ApproveWorkflowHandler:
    """Handler for ApproveWorkflowCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: ApproveWorkflowCommand) -> WorkflowDTO:
        """Approve workflow for execution."""
        CommandValidator.validate_approve_workflow(cmd)
        workflow_id = uuid.UUID(cmd.workflow_id)

        async with self._uow as uow:
            workflow = await uow.workflows.find_by_id(workflow_id)
            if not workflow:
                raise CommandFailed(f"Workflow '{cmd.workflow_id}' not found.")

            workflow.approve()
            await uow.workflows.update(workflow)

        return EntityDTOMapper.workflow_to_dto(workflow)


class ExecuteWorkflowHandler:
    """Handler for ExecuteWorkflowCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: ExecuteWorkflowCommand) -> WorkflowDTO:
        """Execute an approved workflow."""
        CommandValidator.validate_execute_workflow(cmd)
        workflow_id = uuid.UUID(cmd.workflow_id)

        async with self._uow as uow:
            workflow = await uow.workflows.find_by_id(workflow_id)
            if not workflow:
                raise CommandFailed(f"Workflow '{cmd.workflow_id}' not found.")

            workflow.execute()
            await uow.workflows.update(workflow)

        return EntityDTOMapper.workflow_to_dto(workflow)


class AddEvidenceHandler:
    """Handler for AddEvidenceCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: AddEvidenceCommand) -> EvidenceDTO:
        """Attach gathered evidence to workflow."""
        CommandValidator.validate_add_evidence(cmd)
        workflow_id = uuid.UUID(cmd.workflow_id)
        confidence = ConfidenceScore(cmd.confidence_score)

        evidence = Evidence(
            workflow_id=workflow_id,
            source_citation=cmd.source_citation,
            claim_summary=cmd.claim_summary,
            confidence=confidence,
        )

        async with self._uow as uow:
            await uow.evidence.save(evidence)

        return EntityDTOMapper.evidence_to_dto(evidence)


class VerifyEvidenceHandler:
    """Handler for VerifyEvidenceCommand."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: VerifyEvidenceCommand) -> VerificationDTO:
        """Execute claim verification against evidence."""
        CommandValidator.validate_verify_evidence(cmd)
        workflow_id = uuid.UUID(cmd.workflow_id)
        evidence_id = uuid.UUID(cmd.evidence_id)
        status = VerificationStatus(cmd.status)
        confidence = ConfidenceScore(cmd.confidence_score)

        verification = Verification(
            workflow_id=workflow_id,
            evidence_id=evidence_id,
            status=status,
            confidence=confidence,
            notes=cmd.notes,
        )

        async with self._uow as uow:
            await uow.verifications.save(verification)

        return EntityDTOMapper.verification_to_dto(verification)
