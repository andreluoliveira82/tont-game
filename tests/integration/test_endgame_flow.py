"""Integration tests for the endgame flow (no CLI).

Uses the shared ``driver`` / ``moment`` fixtures (see conftest).
"""

import pytest

from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.records import Decision, EndingType
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money


def test_reject_all_then_no_swap_finishes_game(driver, moment) -> None:
    driver.reject_until_endgame(10)
    driver.decide_final_swap(False)

    record = driver.record
    assert driver.state.status is GameStatus.FINISHED
    assert driver.state.is_over() is True
    result = record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITHOUT_SWAP
    assert result.amount_received == Money.of(10)
    assert result.player_briefcase_value == Money.of(10)
    assert record.finished_at == moment
    assert len(record.rounds) == 9
    assert all(r.decision is Decision.REJECT for r in record.rounds)


def test_reject_all_then_swap_finishes_game(driver) -> None:
    driver.reject_until_endgame(10)
    other = driver.state.available_briefcases()[0]
    driver.decide_final_swap(True)

    result = driver.record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITH_SWAP
    assert result.amount_received == other.value
    assert result.final_briefcase_number == other.number
    assert result.player_briefcase_value == Money.of(10)
    assert driver.state.status is GameStatus.FINISHED


def test_endgame_before_final_swap_pending_raises(driver) -> None:
    driver.select(10)
    with pytest.raises(InvalidGameStateError):
        driver.decide_final_swap(True)
    assert driver.record.official_result is None


def test_operation_after_finished_raises(driver) -> None:
    driver.reject_until_endgame(10)
    driver.decide_final_swap(False)
    # Game is FINISHED: a second endgame decision must be rejected by the domain.
    with pytest.raises(InvalidGameStateError):
        driver.decide_final_swap(False)


def test_two_final_briefcases_revealed_not_as_round_openings(driver) -> None:
    driver.reject_until_endgame(10)
    driver.decide_final_swap(True)

    record = driver.record
    total_round_openings = sum(len(r.openings) for r in record.rounds)
    assert total_round_openings == 24
    assert len(driver.state.opened_briefcases()) == 26
    assert driver.state.closed_briefcase_count() == 0
