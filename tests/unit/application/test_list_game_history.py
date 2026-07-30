"""Unit tests for the ListGameHistory use case (Phase 11)."""

from datetime import UTC, datetime
from uuid import uuid4

from tont_game.application.use_cases.list_game_history import ListGameHistory
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import EndingType
from tont_game.domain.history.repository import GameHistorySummary
from tont_game.domain.value_objects.money import Money


def make_summary() -> GameHistorySummary:
    return GameHistorySummary(
        game_id=uuid4(),
        finished_at=datetime(2026, 7, 29, tzinfo=UTC),
        ending_type=EndingType.OFFER_ACCEPTED,
        amount_received=Money.of("100"),
        player_briefcase_value=Money.of("250"),
    )


class FakeRepository:
    def __init__(self, summaries: list[GameHistorySummary]) -> None:
        self._summaries = summaries

    def save(self, record: GameRecord) -> None:  # pragma: no cover - unused here
        raise NotImplementedError

    def list_summaries(self) -> list[GameHistorySummary]:
        return list(self._summaries)


def test_returns_the_repository_summaries() -> None:
    summaries = [make_summary(), make_summary()]
    result = ListGameHistory(FakeRepository(summaries)).execute()
    assert result == summaries


def test_returns_empty_when_there_is_no_history() -> None:
    assert ListGameHistory(FakeRepository([])).execute() == []
