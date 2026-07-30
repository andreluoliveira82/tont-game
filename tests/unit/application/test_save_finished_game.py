"""Unit tests for the SaveFinishedGame use case (Phase 11)."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from tont_game.application.use_cases.save_finished_game import SaveFinishedGame
from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import Decision, OfficialResult
from tont_game.domain.history.repository import GameHistorySummary
from tont_game.domain.value_objects.money import Money


class FakeRepository:
    def __init__(self) -> None:
        self.saved: list[GameRecord] = []

    def save(self, record: GameRecord) -> None:
        self.saved.append(record)

    def list_summaries(self) -> list[GameHistorySummary]:
        return []


def make_finished_record() -> GameRecord:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("250"))],
        seed=7,
    )
    record.record_player_briefcase(1)
    record.record_offer(1, Money.of("100"), Decimal("0.35"), ())
    record.record_decision(1, Decision.ACCEPT)
    record.close(
        OfficialResult.from_accepted_offer(
            decision_round=1,
            accepted_offer=Money.of("100"),
            player_briefcase_value=Money.of("250"),
        ),
        datetime(2026, 7, 29, 1, tzinfo=UTC),
    )
    return record


def test_saves_a_finished_game() -> None:
    repository = FakeRepository()
    record = make_finished_record()
    SaveFinishedGame(repository).execute(record)
    assert repository.saved == [record]


def test_refuses_to_save_an_unfinished_game() -> None:
    repository = FakeRepository()
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100"))],
    )
    with pytest.raises(InvalidGameStateError):
        SaveFinishedGame(repository).execute(record)
    assert repository.saved == []
