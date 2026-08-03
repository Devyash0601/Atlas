"""Unit tests for Domain Value Objects."""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.exceptions.domain_exceptions import ValidationError
from src.domain.value_objects.confidence_score import ConfidenceScore
from src.domain.value_objects.coordinate import Coordinate
from src.domain.value_objects.geo_bounds import GeoBounds
from src.domain.value_objects.research_question import ResearchQuestion
from src.domain.value_objects.time_range import TimeRange


def test_coordinate_valid_and_invalid() -> None:
    """Verify coordinate latitude and longitude validation bounds."""
    coord = Coordinate(latitude=48.8566, longitude=2.3522)
    assert coord.latitude == 48.8566
    assert coord.longitude == 2.3522

    with pytest.raises(ValidationError):
        Coordinate(latitude=91.0, longitude=0.0)

    with pytest.raises(ValidationError):
        Coordinate(latitude=0.0, longitude=-181.0)


def test_geo_bounds_validation() -> None:
    """Verify GeoBounds coordinate consistency."""
    sw = Coordinate(latitude=40.0, longitude=2.0)
    ne = Coordinate(latitude=41.0, longitude=3.0)
    bounds = GeoBounds(south_west=sw, north_east=ne)
    assert bounds.south_west == sw

    # Invalid latitude order
    with pytest.raises(ValidationError):
        GeoBounds(south_west=ne, north_east=sw)


def test_time_range_validation() -> None:
    """Verify TimeRange start date <= end date rule."""
    now = datetime.now(UTC)
    later = now + timedelta(days=10)

    tr = TimeRange(start_date=now, end_date=later)
    assert tr.start_date == now

    with pytest.raises(ValidationError):
        TimeRange(start_date=later, end_date=now)


def test_confidence_score_validation() -> None:
    """Verify ConfidenceScore range [0.0, 1.0]."""
    score = ConfidenceScore(0.85)
    assert score.score == 0.85

    with pytest.raises(ValidationError):
        ConfidenceScore(-0.1)

    with pytest.raises(ValidationError):
        ConfidenceScore(1.05)


def test_research_question_validation() -> None:
    """Verify ResearchQuestion text invariants."""
    q = ResearchQuestion("What is the spatial distribution of UHI in Paris during summer?")
    assert q.text.startswith("What is")

    with pytest.raises(ValidationError):
        ResearchQuestion("Short")

    with pytest.raises(ValidationError):
        ResearchQuestion(" ")
