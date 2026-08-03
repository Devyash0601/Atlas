"""Unit tests for Application DTOs and Mappers."""

import uuid
from datetime import UTC, datetime

from src.application.mappers.entity_dto_mapper import EntityDTOMapper
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
from src.domain.enums.verification_status import VerificationStatus
from src.domain.value_objects.confidence_score import ConfidenceScore
from src.domain.value_objects.coordinate import Coordinate
from src.domain.value_objects.geo_bounds import GeoBounds
from src.domain.value_objects.region_of_interest import RegionOfInterest
from src.domain.value_objects.research_question import ResearchQuestion
from src.domain.value_objects.time_range import TimeRange


def test_entity_to_dto_mappers() -> None:
    """Verify bidirectional entity-to-DTO conversion mapping."""
    user_id = uuid.uuid4()
    sw = Coordinate(latitude=40.0, longitude=2.0)
    ne = Coordinate(latitude=41.0, longitude=3.0)
    roi = RegionOfInterest(name="Region A", bounds=GeoBounds(south_west=sw, north_east=ne))
    question = ResearchQuestion("What is the impact of vegetation on urban temperatures?")

    project = ResearchProject(
        title="UHI Study",
        question=question,
        roi=roi,
        user_id=user_id,
    )

    proj_dto = EntityDTOMapper.project_to_dto(project)
    assert proj_dto.id == str(project.id)
    assert proj_dto.title == "UHI Study"
    assert proj_dto.region_name == "Region A"
    assert proj_dto.south_west_lat == 40.0

    workflow = Workflow(project_id=project.id, planner_output={"step": "1"})
    wf_dto = EntityDTOMapper.workflow_to_dto(workflow)
    assert wf_dto.id == str(workflow.id)
    assert wf_dto.project_id == str(project.id)

    evidence = Evidence(
        workflow_id=workflow.id,
        source_citation="Guide 2024",
        claim_summary="Correlation found",
        confidence=ConfidenceScore(0.9),
    )
    ev_dto = EntityDTOMapper.evidence_to_dto(evidence)
    assert ev_dto.id == str(evidence.id)
    assert ev_dto.confidence_score == 0.9

    verification = Verification(
        workflow_id=workflow.id,
        evidence_id=evidence.id,
        status=VerificationStatus.VERIFIED,
        confidence=ConfidenceScore(0.95),
        notes="All good",
    )
    ver_dto = EntityDTOMapper.verification_to_dto(verification)
    assert ver_dto.id == str(verification.id)

    tr = TimeRange(start_date=datetime.now(UTC), end_date=datetime.now(UTC))
    dataset = Dataset(
        workflow_id=workflow.id,
        satellite=SatelliteType.LANDSAT_C2,
        dataset_type=DatasetType.LAND_SURFACE_TEMPERATURE,
        time_range=tr,
        spatial_resolution_meters=30.0,
    )
    ds_dto = EntityDTOMapper.dataset_to_dto(dataset)
    assert ds_dto.satellite == "landsat_collection_2"

    experiment = Experiment(
        workflow_id=workflow.id,
        parameters={"p": 1},
        status=ExecutionStatus.SUCCESS,
        execution_time_seconds=5.0,
        logs="OK",
    )
    exp_dto = EntityDTOMapper.experiment_to_dto(experiment)
    assert exp_dto.execution_time_seconds == 5.0

    paper = ScientificPaper(
        title="Paper Title",
        authors=["Author 1"],
        year=2024,
        doi="10.1000/1",
        abstract="Abstract text",
    )
    paper_dto = EntityDTOMapper.scientific_paper_to_dto(paper)
    assert paper_dto.doi == "10.1000/1"

    artifact = GeneratedArtifact(
        workflow_id=workflow.id,
        artifact_type=ArtifactType.GEOTIFF,
        file_path="lst.tif",
        size_bytes=100,
    )
    art_dto = EntityDTOMapper.artifact_to_dto(artifact)
    assert art_dto.file_path == "lst.tif"

    report = Report(
        workflow_id=workflow.id,
        markdown_content="# Report",
        export_path="report.md",
    )
    rep_dto = EntityDTOMapper.report_to_dto(report)
    assert rep_dto.export_path == "report.md"

    log = ExecutionLog(
        workflow_id=workflow.id,
        step_name="step_1",
        message="done",
        is_error=False,
    )
    log_dto = EntityDTOMapper.execution_log_to_dto(log)
    assert log_dto.step_name == "step_1"
