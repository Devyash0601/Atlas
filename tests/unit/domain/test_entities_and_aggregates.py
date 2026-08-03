"""Unit tests for Domain Entities and Aggregate Roots."""

import uuid
from datetime import UTC, datetime

import pytest

from src.domain.base.value_object import ValueObject
from src.domain.entities.dataset import Dataset
from src.domain.entities.evidence import Evidence
from src.domain.entities.execution_log import ExecutionLog
from src.domain.entities.experiment import Experiment
from src.domain.entities.generated_artifact import GeneratedArtifact
from src.domain.entities.report import Report
from src.domain.entities.research_project import ResearchProject
from src.domain.entities.scientific_paper import ScientificPaper
from src.domain.entities.verification import Verification
from src.domain.entities.workflow import Workflow
from src.domain.enums.artifact_type import ArtifactType, ExecutionStatus
from src.domain.enums.dataset_type import DatasetType, SatelliteType
from src.domain.enums.project_status import ProjectStatus
from src.domain.enums.verification_status import VerificationStatus
from src.domain.enums.workflow_status import WorkflowStatus
from src.domain.events.project_events import ProjectCreated, WorkflowCreated, WorkflowExecuted
from src.domain.events.report_events import ReportGenerated
from src.domain.events.verification_events import EvidenceAdded, VerificationCompleted
from src.domain.exceptions.domain_exceptions import (
    BusinessRuleViolationError,
    StateTransitionError,
    ValidationError,
)
from src.domain.value_objects.confidence_score import ConfidenceScore
from src.domain.value_objects.coordinate import Coordinate
from src.domain.value_objects.geo_bounds import GeoBounds
from src.domain.value_objects.region_of_interest import RegionOfInterest
from src.domain.value_objects.research_question import ResearchQuestion
from src.domain.value_objects.time_range import TimeRange


def test_research_project_lifecycle_and_events() -> None:
    """Verify ResearchProject aggregate state transitions and ProjectCreated event generation."""
    sw = Coordinate(latitude=48.0, longitude=2.0)
    ne = Coordinate(latitude=49.0, longitude=3.0)
    roi = RegionOfInterest(name="Paris", bounds=GeoBounds(south_west=sw, north_east=ne))
    question = ResearchQuestion("Analyze urban heat island intensity in Paris region.")
    user_id = uuid.uuid4()

    project = ResearchProject(
        title="Paris UHI Study",
        question=question,
        roi=roi,
        user_id=user_id,
    )

    assert project.title == "Paris UHI Study"
    assert project.question == question
    assert project.roi == roi
    assert project.user_id == user_id
    assert project.status == ProjectStatus.CREATED

    events = project.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], ProjectCreated)
    assert events[0].project_id == project.id
    assert events[0].title == "Paris UHI Study"

    # Test dictionary serialization
    serialized = project.to_dict()
    assert serialized["id"] == str(project.id)
    assert serialized["title"] == "Paris UHI Study"

    # Test valid state transition
    project.transition_to(ProjectStatus.PLANNED)
    assert project.status == ProjectStatus.PLANNED

    project.transition_to(ProjectStatus.RUNNING)
    assert project.status == ProjectStatus.RUNNING

    project.transition_to(ProjectStatus.COMPLETED)
    assert project.status == ProjectStatus.COMPLETED

    # Test invalid state transition from COMPLETED
    with pytest.raises(StateTransitionError):
        project.transition_to(ProjectStatus.RUNNING)

    with pytest.raises(ValidationError):
        ResearchProject(title="  ", question=question, roi=roi, user_id=user_id)


def test_workflow_approval_execution_rule() -> None:
    """Verify Business Rule: Workflow CANNOT execute before human approval."""
    project_id = uuid.uuid4()
    plan_output = {"steps": ["download", "calculate_lst"]}
    workflow = Workflow(
        project_id=project_id,
        planner_output=plan_output,
    )

    assert workflow.project_id == project_id
    assert workflow.planner_output == plan_output
    assert workflow.status == WorkflowStatus.DRAFT

    # Executing unapproved workflow must fail
    with pytest.raises(BusinessRuleViolationError):
        workflow.execute()

    with pytest.raises(StateTransitionError):
        workflow.mark_completed()

    # Approve and execute successfully
    workflow.approve()
    assert workflow.status == WorkflowStatus.APPROVED

    with pytest.raises(StateTransitionError):
        workflow.approve()

    workflow.execute()
    assert workflow.status == WorkflowStatus.EXECUTING

    workflow.mark_completed()
    assert workflow.status == WorkflowStatus.COMPLETED

    # Test mark_failed
    w2 = Workflow(project_id=project_id, planner_output={})
    w2.mark_failed()
    assert w2.status == WorkflowStatus.FAILED


def test_evidence_source_invariant() -> None:
    """Verify Business Rule: Evidence cannot exist without a valid source citation."""
    workflow_id = uuid.uuid4()
    score = ConfidenceScore(0.9)

    evidence = Evidence(
        workflow_id=workflow_id,
        source_citation="Smith et al. 2024 Remote Sensing Environment",
        claim_summary="LST is negatively correlated with NDVI in urban centers.",
        confidence=score,
    )
    assert evidence.workflow_id == workflow_id
    assert evidence.source_citation.startswith("Smith et al.")
    assert evidence.claim_summary.startswith("LST is negatively")
    assert evidence.confidence == score

    with pytest.raises(BusinessRuleViolationError):
        Evidence(
            workflow_id=workflow_id,
            source_citation="   ",
            claim_summary="Unsupported claim",
            confidence=score,
        )

    with pytest.raises(BusinessRuleViolationError):
        Evidence(
            workflow_id=workflow_id,
            source_citation="Valid citation",
            claim_summary=" ",
            confidence=score,
        )


def test_dataset_entity_properties() -> None:
    """Verify Dataset entity initialization and properties."""
    wf_id = uuid.uuid4()
    tr = TimeRange(start_date=datetime.now(UTC), end_date=datetime.now(UTC))
    ds = Dataset(
        workflow_id=wf_id,
        satellite=SatelliteType.LANDSAT_C2,
        dataset_type=DatasetType.LAND_SURFACE_TEMPERATURE,
        time_range=tr,
        spatial_resolution_meters=30.0,
    )
    assert ds.workflow_id == wf_id
    assert ds.satellite == SatelliteType.LANDSAT_C2
    assert ds.dataset_type == DatasetType.LAND_SURFACE_TEMPERATURE
    assert ds.time_range == tr
    assert ds.spatial_resolution_meters == 30.0


def test_experiment_entity_properties() -> None:
    """Verify Experiment entity initialization and properties."""
    wf_id = uuid.uuid4()
    exp = Experiment(
        workflow_id=wf_id,
        parameters={"kernel_size": 3},
        status=ExecutionStatus.SUCCESS,
        execution_time_seconds=12.5,
        logs="OK",
    )
    assert exp.workflow_id == wf_id
    assert exp.parameters == {"kernel_size": 3}
    assert exp.status == ExecutionStatus.SUCCESS
    assert exp.execution_time_seconds == 12.5
    assert exp.logs == "OK"


def test_verification_entity_properties() -> None:
    """Verify Verification entity properties."""
    wf_id = uuid.uuid4()
    ev_id = uuid.uuid4()
    cs = ConfidenceScore(0.95)
    ver = Verification(
        workflow_id=wf_id,
        evidence_id=ev_id,
        status=VerificationStatus.VERIFIED,
        confidence=cs,
        notes="Matches Landsat 8 thermal band.",
    )
    assert ver.workflow_id == wf_id
    assert ver.evidence_id == ev_id
    assert ver.status == VerificationStatus.VERIFIED
    assert ver.confidence == cs
    assert ver.notes == "Matches Landsat 8 thermal band."


def test_scientific_paper_entity_properties() -> None:
    """Verify ScientificPaper entity properties."""
    paper = ScientificPaper(
        title="Urban Surface Energy Balance",
        authors=["Alice Curie", "Bob Einstein"],
        year=2024,
        doi="10.1016/j.rse.2024.10001",
        abstract="Study of thermal anisotropy.",
    )
    assert paper.title == "Urban Surface Energy Balance"
    assert paper.authors == ["Alice Curie", "Bob Einstein"]
    assert paper.year == 2024
    assert paper.doi == "10.1016/j.rse.2024.10001"
    assert paper.abstract == "Study of thermal anisotropy."


def test_generated_artifact_and_report_entities() -> None:
    """Verify GeneratedArtifact and Report entity properties."""
    wf_id = uuid.uuid4()
    art = GeneratedArtifact(
        workflow_id=wf_id,
        artifact_type=ArtifactType.GEOTIFF,
        file_path="exports/lst.tif",
        size_bytes=1048576,
    )
    assert art.workflow_id == wf_id
    assert art.artifact_type == ArtifactType.GEOTIFF
    assert art.file_path == "exports/lst.tif"
    assert art.size_bytes == 1048576

    rep = Report(
        workflow_id=wf_id,
        markdown_content="# Paris UHI Report",
        export_path="exports/report.md",
    )
    assert rep.workflow_id == wf_id
    assert rep.markdown_content == "# Paris UHI Report"
    assert rep.export_path == "exports/report.md"

    log = ExecutionLog(
        workflow_id=wf_id,
        step_name="thermal_calibration",
        message="Calibrated band 10",
        is_error=False,
    )
    assert log.workflow_id == wf_id
    assert log.step_name == "thermal_calibration"
    assert log.message == "Calibrated band 10"
    assert not log.is_error


def test_domain_event_classes() -> None:
    """Verify Domain Event classes initialization."""
    wf_id = uuid.uuid4()
    p_id = uuid.uuid4()

    wfc = WorkflowCreated(workflow_id=wf_id, project_id=p_id)
    assert wfc.workflow_id == wf_id

    wfe = WorkflowExecuted(workflow_id=wf_id, status=WorkflowStatus.COMPLETED)
    assert wfe.status == WorkflowStatus.COMPLETED

    ea = EvidenceAdded(evidence_id=p_id, workflow_id=wf_id, source_citation="DOI:10.1000")
    assert ea.source_citation == "DOI:10.1000"

    vc = VerificationCompleted(
        verification_id=p_id,
        workflow_id=wf_id,
        status=VerificationStatus.VERIFIED,
        confidence_score=0.9,
    )
    assert vc.confidence_score == 0.9

    rg = ReportGenerated(report_id=p_id, workflow_id=wf_id, markdown_path="out.md")
    assert rg.markdown_path == "out.md"


class ConcreteValueObject(ValueObject):
    def __init__(self, val: int) -> None:
        self.val = val


def test_value_object_base_methods() -> None:
    """Verify ValueObject base equality, hashing, and repr."""
    v1 = ConcreteValueObject(42)
    v2 = ConcreteValueObject(42)
    v3 = ConcreteValueObject(99)

    assert v1 == v2
    assert v1 != v3
    assert v1 != "not_a_vo"
    assert hash(v1) == hash(v2)
    assert "ConcreteValueObject(val=42)" in repr(v1)
