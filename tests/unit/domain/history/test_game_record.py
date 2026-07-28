"""Unit tests for the append-only GameRecord."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from tont_game.domain.errors import HistoryError, OfficialResultAlreadySetError
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import (
    BriefcaseOpeningRecord,
    Decision,
    OfficialResult,
)
from tont_game.domain.value_objects.money import Money


def make_record() -> GameRecord:
    return GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 28, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("200"))],
        seed=42,
    )


def test_initial_fields() -> None:
    record = make_record()
    assert record.seed == 42
    assert record.initial_distribution == ((1, Money.of("100")), (2, Money.of("200")))
    assert record.player_briefcase_number is None
    assert record.official_result is None
    assert record.finished_at is None
    assert record.rounds == ()


def test_rounds_group_openings_offer_and_decision() -> None:
    record = make_record()
    record.record_opening(1, 5, Money.of("50"))
    record.record_offer(1, Money.of("30"), Decimal("0.35"), (Money.of("50"),))
    record.record_decision(1, Decision.REJECT)
    rounds = record.rounds
    assert len(rounds) == 1
    assert rounds[0].round_number == 1
    assert rounds[0].openings[0].briefcase_number == 5
    assert rounds[0].offer is not None
    assert rounds[0].offer.percentage == Decimal("0.35")
    assert rounds[0].decision is Decision.REJECT


def test_player_briefcase_is_recorded_once() -> None:
    record = make_record()
    record.record_player_briefcase(7)
    assert record.player_briefcase_number == 7
    with pytest.raises(HistoryError):
        record.record_player_briefcase(8)


def test_offer_is_write_once_per_round() -> None:
    record = make_record()
    record.record_offer(1, Money.of("30"), Decimal("0.35"), ())
    with pytest.raises(HistoryError):
        record.record_offer(1, Money.of("40"), Decimal("0.40"), ())


def test_decision_is_write_once_per_round() -> None:
    record = make_record()
    record.record_decision(1, Decision.REJECT)
    with pytest.raises(HistoryError):
        record.record_decision(1, Decision.ACCEPT)


def test_recorded_rounds_are_immutable() -> None:
    record = make_record()
    record.record_opening(1, 5, Money.of("50"))
    round_record = record.rounds[0]
    with pytest.raises(FrozenInstanceError):
        round_record.round_number = 2  # type: ignore[misc]


def test_history_cannot_be_altered_retroactively_via_handed_out_round() -> None:
    record = make_record()
    record.record_opening(1, 5, Money.of("50"))
    handed_out = record.rounds[0]
    # with_opening returns a new instance; the record's own history is untouched.
    handed_out.with_opening(BriefcaseOpeningRecord(9, Money.of("9")))
    assert len(record.rounds[0].openings) == 1


def test_close_sets_official_result_write_once() -> None:
    record = make_record()
    result = OfficialResult.from_accepted_offer(1, Money.of("30"), Money.of("100"))
    record.close(result, datetime(2026, 7, 28, 1, tzinfo=UTC))
    assert record.official_result is result
    assert record.finished_at == datetime(2026, 7, 28, 1, tzinfo=UTC)
    with pytest.raises(OfficialResultAlreadySetError):
        record.close(result, datetime(2026, 7, 28, 2, tzinfo=UTC))
