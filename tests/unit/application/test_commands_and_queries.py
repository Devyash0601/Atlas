"""Unit tests for Application Commands, Queries, and Validators."""

import uuid

import pytest

from src.application.commands.evidence_commands import AddEvidenceCommand, VerifyEvidenceCommand
from src.application.commands.project_commands import (
    ApproveWorkflowCommand,
    CreateProjectCommand,
    CreateWorkflowCommand,
    ExecuteWorkflowCommand,
)
from src.application.exceptions.application_exceptions import ValidationFailed
from src.application.queries.project_queries import (
    GetProjectQuery,
    GetReportQuery,
    GetWorkflowQuery,
    ListDatasetsQuery,
    ListEvidenceQuery,
    ListProjectsQuery,
    SearchScientificPapersQuery,
)
from src.application.validators.command_validators import CommandValidator


def test_command_validator_success() -> None:
    """Verify CommandValidator passes valid commands."""
    user_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    evidence_id = str(uuid.uuid4())

    cmd_proj = CreateProjectCommand(
        title="Paris UHI Study",
        question_text="How does vegetation index correlate with surface temperature in Paris?",
        region_name="Paris Metropolitan",
        south_west_lat=48.5,
        south_west_lon=2.2,
        north_east_lat=49.0,
        north_east_lon=2.5,
        user_id=user_id,
    )
    CommandValidator.validate_create_project(cmd_proj)

    cmd_wf = CreateWorkflowCommand(project_id=project_id, planner_output={"step": "calibrate"})
    CommandValidator.validate_create_workflow(cmd_wf)

    cmd_app = ApproveWorkflowCommand(workflow_id=workflow_id, approver_user_id=user_id)
    CommandValidator.validate_approve_workflow(cmd_app)

    cmd_exe = ExecuteWorkflowCommand(workflow_id=workflow_id)
    CommandValidator.validate_execute_workflow(cmd_exe)

    cmd_ev = AddEvidenceCommand(
        workflow_id=workflow_id,
        source_citation="Landsat 8 Band 10 calibration guide",
        claim_summary="Calibrated LST shows +3K delta.",
        confidence_score=0.92,
    )
    CommandValidator.validate_add_evidence(cmd_ev)

    cmd_ver = VerifyEvidenceCommand(
        workflow_id=workflow_id,
        evidence_id=evidence_id,
        status="verified",
        confidence_score=0.95,
    )
    CommandValidator.validate_verify_evidence(cmd_ver)


def test_command_validator_failures() -> None:
    """Verify CommandValidator raises ValidationFailed on invalid inputs."""
    user_id = str(uuid.uuid4())

    # Empty title
    with pytest.raises(ValidationFailed):
        CommandValidator.validate_create_project(
            CreateProjectCommand(
                title="",
                question_text="Valid question text",
                region_name="Region",
                south_west_lat=40.0,
                south_west_lon=2.0,
                north_east_lat=41.0,
                north_east_lon=3.0,
                user_id=user_id,
            )
        )

    # Invalid latitude ordering
    with pytest.raises(ValidationFailed):
        CommandValidator.validate_create_project(
            CreateProjectCommand(
                title="Title",
                question_text="Valid question text",
                region_name="Region",
                south_west_lat=41.0,
                south_west_lon=2.0,
                north_east_lat=40.0,
                north_east_lon=3.0,
                user_id=user_id,
            )
        )

    # Invalid UUID
    with pytest.raises(ValidationFailed):
        cmd = CreateWorkflowCommand(project_id="not_a_uuid", planner_output={})
        CommandValidator.validate_create_workflow(cmd)


def test_queries_instantiation() -> None:
    """Verify Query object creation."""
    u_id = str(uuid.uuid4())
    p_id = str(uuid.uuid4())
    w_id = str(uuid.uuid4())

    q1 = GetProjectQuery(project_id=p_id)
    assert q1.project_id == p_id

    q2 = ListProjectsQuery(user_id=u_id, limit=20, offset=0)
    assert q2.user_id == u_id

    q3 = GetWorkflowQuery(workflow_id=w_id)
    assert q3.workflow_id == w_id

    q4 = ListDatasetsQuery(workflow_id=w_id)
    assert q4.workflow_id == w_id

    q5 = ListEvidenceQuery(workflow_id=w_id)
    assert q5.workflow_id == w_id

    q6 = GetReportQuery(workflow_id=w_id)
    assert q6.workflow_id == w_id

    q7 = SearchScientificPapersQuery(query_text="Landsat UHI", limit=5)
    assert q7.query_text == "Landsat UHI"
