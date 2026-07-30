"""Unit tests for the GetGameHistoryDetail use case (Phase 12)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from tont_game.application.use_cases.get_game_history_detail import (
    GetGameHistoryDetail,
)
from tont_game.domain.history.records import EndingType
from tont_game.domain.history.repository import (
    GameHistoryDetail,
    GameHistorySummary,
)
from tont_game.domain.value_objects.money import Money


def a_detail(game_id: UUID) -> GameHistoryDetail:
    return GameHistoryDetail(
        game_id=game_id,
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        finished_at=datetime(2026, 7, 29, 1, tzinfo=UTC),
        seed=7,
        player_briefcase=2,
        ending_type=EndingType.OFFER_ACCEPTED,
        amount_received=Money.of("120.50"),
        player_briefcase_value=Money.of("250"),
        rounds=(),
    )


class StubRepository:
    def __init__(self, detail: GameHistoryDetail | None) -> None:
        self._detail = detail
        self.requested: UUID | None = None

    def save(self, record: object) -> None:  # pragma: no cover - unused here
        raise NotImplementedError

    def list_summaries(self) -> list[GameHistorySummary]:  # pragma: no cover
        raise NotImplementedError

    def get(self, game_id: UUID) -> GameHistoryDetail | None:
        self.requested = game_id
        return self._detail


def test_returns_the_detail_from_the_repository() -> None:
    game_id = uuid4()
    repository = StubRepository(a_detail(game_id))
    result = GetGameHistoryDetail(repository).execute(game_id)
    assert result is not None
    assert result.game_id == game_id
    assert repository.requested == game_id


def test_returns_none_when_not_found() -> None:
    assert GetGameHistoryDetail(StubRepository(None)).execute(uuid4()) is None
