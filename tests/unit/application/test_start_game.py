"""Unit tests for the StartGame use case."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID

from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")


class FakeClock:
    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


class FakeIdGenerator:
    def __init__(self, game_id: UUID) -> None:
        self._id = game_id

    def new_id(self) -> UUID:
        return self._id


class IdentityRandomSource:
    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


def test_start_game_initializes_session_and_record() -> None:
    moment = datetime(2026, 7, 28, tzinfo=UTC)
    game_id = UUID("00000000-0000-0000-0000-000000000001")
    values = [Money.of(n) for n in range(1, 27)]

    session = StartGame(FakeClock(moment), FakeIdGenerator(game_id)).execute(
        IdentityRandomSource(), seed=99, values=values
    )

    record = session.game_record
    assert record.game_id == game_id
    assert record.started_at == moment
    assert record.seed == 99
    assert record.initial_distribution == tuple((n, Money.of(n)) for n in range(1, 27))
    assert session.game_state.closed_briefcase_count() == 26
    assert record.official_result is None


def test_seed_is_optional() -> None:
    session = StartGame(
        FakeClock(datetime(2026, 7, 28, tzinfo=UTC)),
        FakeIdGenerator(UUID(int=2)),
    ).execute(IdentityRandomSource())
    assert session.game_record.seed is None
