"""Unit tests for the RoundSchedule value object."""

import pytest

from tont_game.domain.value_objects.round_schedule import (
    DEFAULT_ROUND_OPENINGS,
    RoundSchedule,
)


def test_default_schedule_has_nine_rounds() -> None:
    schedule = RoundSchedule()
    assert schedule.total_rounds == 9
    assert schedule.openings == (6, 5, 4, 3, 2, 1, 1, 1, 1)


def test_default_schedule_opens_twenty_four_briefcases() -> None:
    assert RoundSchedule().total_openings == 24


def test_default_schedule_leaves_two_closed_from_twenty_six() -> None:
    # 26 total - 24 opened = 2 closed (player + last briefcase).
    assert 26 - RoundSchedule().total_openings == 2


def test_openings_for_each_round() -> None:
    schedule = RoundSchedule()
    assert [schedule.openings_for_round(r) for r in range(1, 10)] == list(
        DEFAULT_ROUND_OPENINGS
    )


def test_openings_for_round_out_of_range() -> None:
    schedule = RoundSchedule()
    with pytest.raises(ValueError):
        schedule.openings_for_round(0)
    with pytest.raises(ValueError):
        schedule.openings_for_round(10)


def test_schedule_rejects_empty() -> None:
    with pytest.raises(ValueError):
        RoundSchedule(openings=())


def test_schedule_rejects_non_positive_round() -> None:
    with pytest.raises(ValueError):
        RoundSchedule(openings=(3, 0, 1))
