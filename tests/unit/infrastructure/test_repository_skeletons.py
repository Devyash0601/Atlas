"""Unit tests verifying Repository Skeletons raise NotImplementedError on persistence calls."""

import uuid

import pytest

from src.infrastructure.repositories.repository_impls import (
    DatasetRepositoryImpl,
    EvidenceRepositoryImpl,
    ExecutionLogRepositoryImpl,
    ExperimentRepositoryImpl,
    ProjectRepositoryImpl,
    ReportRepositoryImpl,
    ScientificPaperRepositoryImpl,
    VerificationRepositoryImpl,
    WorkflowRepositoryImpl,
)


@pytest.mark.asyncio
async def test_repository_skeletons_raise_not_implemented() -> None:
    """Verify repository implementation skeletons raise NotImplementedError."""
    dummy_id = uuid.uuid4()

    proj_repo = ProjectRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await proj_repo.find_by_id(dummy_id)

    wf_repo = WorkflowRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await wf_repo.find_by_id(dummy_id)

    ds_repo = DatasetRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await ds_repo.find_by_id(dummy_id)

    ev_repo = EvidenceRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await ev_repo.find_by_id(dummy_id)

    rep_repo = ReportRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await rep_repo.find_by_id(dummy_id)

    exp_repo = ExperimentRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await exp_repo.find_by_id(dummy_id)

    ver_repo = VerificationRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await ver_repo.find_by_id(dummy_id)

    paper_repo = ScientificPaperRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await paper_repo.find_by_id(dummy_id)

    log_repo = ExecutionLogRepositoryImpl()
    with pytest.raises(NotImplementedError):
        await log_repo.save(None)  # type: ignore[arg-type]
