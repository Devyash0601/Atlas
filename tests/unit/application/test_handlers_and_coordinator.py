"""Unit tests for Command Handlers, Workflow Coordinator, and Application Services."""

import uuid

import pytest

from src.application.commands.evidence_commands import AddEvidenceCommand, VerifyEvidenceCommand
from src.application.commands.project_commands import (
    ApproveWorkflowCommand,
    CreateProjectCommand,
    CreateWorkflowCommand,
    ExecuteWorkflowCommand,
)
from src.application.exceptions.application_exceptions import QueryFailed
from src.application.services.application_services import (
    ProjectApplicationService,
    WorkflowApplicationService,
)
from src.application.transactions.unit_of_work import UnitOfWork
from src.application.workflows.workflow_coordinator import WorkflowCoordinator
from src.domain.base.entity import Entity
from src.domain.base.repository import Repository
from src.domain.entities.dataset import Dataset
from src.domain.entities.evidence import Evidence
from src.domain.entities.experiment import Experiment
from src.domain.entities.report import Report
from src.domain.entities.research_project import ResearchProject
from src.domain.entities.scientific_paper import ScientificPaper
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow
from src.domain.repositories.interfaces import (
    DatasetRepository,
    EvidenceRepository,
    ExperimentRepository,
    ProjectRepository,
    ReportRepository,
    ScientificPaperRepository,
    VerificationRepository,
    WorkflowRepository,
)


class InMemoryRepository[T: Entity](Repository[T]):
    """Generic in-memory repository implementation for unit testing."""

    def __init__(self) -> None:
        self._storage: dict[uuid.UUID, T] = {}

    async def save(self, entity: T) -> None:
        self._storage[entity.id] = entity

    async def update(self, entity: T) -> None:
        self._storage[entity.id] = entity

    async def delete(self, entity_id: uuid.UUID) -> None:
        self._storage.pop(entity_id, None)

    async def find_by_id(self, entity_id: uuid.UUID) -> T | None:
        return self._storage.get(entity_id)

    async def find_many(self, limit: int = 100, offset: int = 0) -> list[T]:
        items = list(self._storage.values())
        return items[offset : offset + limit]

    async def exists(self, entity_id: uuid.UUID) -> bool:
        return entity_id in self._storage

    async def count(self) -> int:
        return len(self._storage)


class InMemoryProjectRepository(InMemoryRepository[ResearchProject], ProjectRepository):
    async def find_by_user_id(self, user_id: uuid.UUID) -> list[ResearchProject]:
        return [p for p in self._storage.values() if p.user_id == user_id]


class InMemoryWorkflowRepository(InMemoryRepository[Workflow], WorkflowRepository):
    async def find_by_project_id(self, project_id: uuid.UUID) -> list[Workflow]:
        return [w for w in self._storage.values() if w.project_id == project_id]


class InMemoryDatasetRepository(InMemoryRepository[Dataset], DatasetRepository):
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Dataset]:
        return [d for d in self._storage.values() if d.workflow_id == workflow_id]


class InMemoryEvidenceRepository(InMemoryRepository[Evidence], EvidenceRepository):
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Evidence]:
        return [e for e in self._storage.values() if e.workflow_id == workflow_id]


class InMemoryReportRepository(InMemoryRepository[Report], ReportRepository):
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> Report | None:
        for r in self._storage.values():
            if r.workflow_id == workflow_id:
                return r
        return None


class InMemoryExperimentRepository(InMemoryRepository[Experiment], ExperimentRepository):
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Experiment]:
        return [ex for ex in self._storage.values() if ex.workflow_id == workflow_id]


class InMemoryVerificationRepository(InMemoryRepository[Verification], VerificationRepository):
    async def find_by_workflow_id(self, workflow_id: uuid.UUID) -> list[Verification]:
        return [v for v in self._storage.values() if v.workflow_id == workflow_id]


class InMemoryScientificPaperRepository(
    InMemoryRepository[ScientificPaper], ScientificPaperRepository
):
    async def find_by_doi(self, doi: str) -> ScientificPaper | None:
        for p in self._storage.values():
            if p.doi == doi:
                return p
        return None


class MockUnitOfWork(UnitOfWork):
    """In-memory UnitOfWork implementation for testing application use cases."""

    def __init__(self) -> None:
        self.projects = InMemoryProjectRepository()
        self.workflows = InMemoryWorkflowRepository()
        self.datasets = InMemoryDatasetRepository()
        self.evidence = InMemoryEvidenceRepository()
        self.reports = InMemoryReportRepository()
        self.experiments = InMemoryExperimentRepository()
        self.verifications = InMemoryVerificationRepository()
        self.papers = InMemoryScientificPaperRepository()

    async def begin(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


@pytest.mark.asyncio
async def test_workflow_coordinator_end_to_end_flow() -> None:
    """Verify WorkflowCoordinator end-to-end orchestration flow and application events."""
    uow = MockUnitOfWork()
    coordinator = WorkflowCoordinator(uow)
    user_id = str(uuid.uuid4())

    # 1. Create Project
    cmd_proj = CreateProjectCommand(
        title="Paris UHI Study",
        question_text="How does vegetation cover impact summer land surface temperatures?",
        region_name="Paris Region",
        south_west_lat=48.5,
        south_west_lon=2.2,
        north_east_lat=49.0,
        north_east_lon=2.5,
        user_id=user_id,
    )
    proj_dto = await coordinator.create_project(cmd_proj)
    assert proj_dto.title == "Paris UHI Study"
    assert proj_dto.status == "created"

    # 2. Create Workflow
    cmd_wf = CreateWorkflowCommand(
        project_id=proj_dto.id,
        planner_output={"steps": ["download_landsat", "calculate_ndvi", "calculate_lst"]},
    )
    wf_dto = await coordinator.create_workflow(cmd_wf)
    assert wf_dto.project_id == proj_dto.id
    assert wf_dto.status == "draft"

    # 3. Approve Workflow
    cmd_app = ApproveWorkflowCommand(workflow_id=wf_dto.id, approver_user_id=user_id)
    wf_approved_dto = await coordinator.approve_workflow(cmd_app)
    assert wf_approved_dto.status == "approved"

    # 4. Execute Workflow
    cmd_exe = ExecuteWorkflowCommand(workflow_id=wf_dto.id)
    wf_exec_dto = await coordinator.execute_workflow(cmd_exe)
    assert wf_exec_dto.status == "executing"

    # 5. Add Evidence
    cmd_ev = AddEvidenceCommand(
        workflow_id=wf_dto.id,
        source_citation="Landsat 8 Collection 2 Guide",
        claim_summary="Negative linear correlation between NDVI and LST in urban areas.",
        confidence_score=0.91,
    )
    ev_dto = await coordinator.add_evidence(cmd_ev)
    assert ev_dto.confidence_score == 0.91

    # 6. Verify Evidence
    cmd_ver = VerifyEvidenceCommand(
        workflow_id=wf_dto.id,
        evidence_id=ev_dto.id,
        status="verified",
        confidence_score=0.96,
        notes="Validated against 2024 weather station data.",
    )
    ver_dto = await coordinator.verify_evidence(cmd_ver)
    assert ver_dto.status == "verified"

    # Check Dispatched Application Events
    events = coordinator.get_dispatched_events()
    assert len(events) == 4  # ProjectStarted, WorkflowApproved, WorkflowCompleted, EvidenceVerified


@pytest.mark.asyncio
async def test_workflow_application_service() -> None:
    """Verify WorkflowApplicationService queries."""
    uow = MockUnitOfWork()
    service = WorkflowApplicationService(uow)
    proj_service = ProjectApplicationService(uow)
    assert proj_service.coordinator is not None

    with pytest.raises(QueryFailed):
        await service.get_workflow_dto("not_a_uuid")

    with pytest.raises(QueryFailed):
        await service.get_workflow_dto(str(uuid.uuid4()))
