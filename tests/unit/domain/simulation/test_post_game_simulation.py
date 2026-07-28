"""Unit tests for the post-game simulation domain service (Phase 6)."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import Decision, OfficialResult
from tont_game.domain.simulation.post_game_simulation import (
    SimulationResult,
    SimulationScenario,
    simulate_continue_hold,
)
from tont_game.domain.value_objects.money import Money


def make_record_with_topa(
    accepted: str = "100.00", player_value: str = "250.00"
) -> GameRecord:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 28, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("250"))],
        seed=7,
    )
    record.record_player_briefcase(1)
    record.record_offer(1, Money.of(accepted), Decimal("0.35"), ())
    record.record_decision(1, Decision.ACCEPT)
    record.close(
        OfficialResult.from_accepted_offer(
            decision_round=1,
            accepted_offer=Money.of(accepted),
            player_briefcase_value=Money.of(player_value),
        ),
        datetime(2026, 7, 28, 1, tzinfo=UTC),
    )
    return record


def test_topa_produces_continue_hold_result() -> None:
    record = make_record_with_topa(accepted="100.00", player_value="250.00")
    result = simulate_continue_hold(record)
    assert isinstance(result, SimulationResult)
    assert result.scenario is SimulationScenario.CONTINUE_HOLD
    assert result.hypothetical_amount == Money.of("250.00")
    assert result.official_amount == Money.of("100.00")


def test_hypothetical_amount_is_player_briefcase_value() -> None:
    record = make_record_with_topa(accepted="1.00", player_value="500000.00")
    assert record.official_result is not None
    result = simulate_continue_hold(record)
    assert result.hypothetical_amount == record.official_result.player_briefcase_value


def test_official_amount_is_amount_received() -> None:
    record = make_record_with_topa(accepted="1.00", player_value="500000.00")
    assert record.official_result is not None
    result = simulate_continue_hold(record)
    assert result.official_amount == record.official_result.amount_received


def test_simulation_is_deterministic() -> None:
    record = make_record_with_topa()
    assert simulate_continue_hold(record) == simulate_continue_hold(record)


def test_simulation_does_not_change_game_record() -> None:
    record = make_record_with_topa()
    official_before = record.official_result
    rounds_before = record.rounds
    simulate_continue_hold(record)
    assert record.official_result is official_before
    assert record.rounds == rounds_before
    assert record.finished_at == datetime(2026, 7, 28, 1, tzinfo=UTC)


def test_simulation_does_not_change_official_result() -> None:
    record = make_record_with_topa(accepted="100.00", player_value="250.00")
    official = record.official_result
    assert official is not None
    simulate_continue_hold(record)
    assert official.amount_received == Money.of("100.00")
    assert official.player_briefcase_value == Money.of("250.00")


def test_missing_official_result_raises() -> None:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 28, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100"))],
    )
    with pytest.raises(InvalidGameStateError):
        simulate_continue_hold(record)


def test_simulation_result_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    result = simulate_continue_hold(make_record_with_topa())
    with pytest.raises(FrozenInstanceError):
        result.official_amount = Money.of("1")  # type: ignore[misc]


def test_derived_helpers_do_not_use_signed_money() -> None:
    record = make_record_with_topa(accepted="100.00", player_value="250.00")
    result = simulate_continue_hold(record)
    assert result.absolute_difference() == Money.of("150.00")
    assert result.hypothetical_is_higher() is True
