"""Integration tests for the Phase 5.5 endgame flow (no CLI)."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

import pytest

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_final_swap import DecideFinalSwap
from tont_game.application.use_cases.decide_offer import DecideOffer
from tont_game.application.use_cases.open_briefcase import OpenBriefcase
from tont_game.application.use_cases.process_banker_offer import ProcessBankerOffer
from tont_game.application.use_cases.select_initial_briefcase import (
    SelectInitialBriefcase,
)
from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.records import Decision, EndingType
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")
MOMENT = datetime(2026, 7, 28, 18, 0, tzinfo=UTC)


class FakeClock:
    def now(self) -> datetime:
        return MOMENT


class FakeIdGenerator:
    def new_id(self) -> UUID:
        return uuid4()


class IdentityRandomSource:
    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


def start_session() -> GameSession:
    values = [Money.of(n) for n in range(1, 27)]
    return StartGame(FakeClock(), FakeIdGenerator()).execute(
        IdentityRandomSource(), seed=1, values=values
    )


def open_full_round(session: GameSession) -> None:
    state = session.game_state
    to_open = state.openings_required_in_current_round()
    opener = OpenBriefcase()
    for briefcase in state.available_briefcases()[:to_open]:
        opener.execute(session, briefcase.number)


def reach_endgame(session: GameSession, player: int = 10) -> None:
    SelectInitialBriefcase().execute(session, player)
    strategy = DefaultBankerStrategy()
    clock = FakeClock()
    while session.game_state.status is not GameStatus.FINAL_SWAP_PENDING:
        open_full_round(session)
        ProcessBankerOffer(strategy).execute(session)
        DecideOffer(clock).execute(session, Decision.REJECT)


def test_reject_all_then_no_swap_finishes_game() -> None:
    session = start_session()
    reach_endgame(session)
    DecideFinalSwap(FakeClock()).execute(session, False)

    record = session.game_record
    assert session.game_state.status is GameStatus.FINISHED
    assert session.game_state.is_over() is True
    result = record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITHOUT_SWAP
    assert result.amount_received == Money.of(10)
    assert result.player_briefcase_value == Money.of(10)
    assert record.finished_at == MOMENT
    assert len(record.rounds) == 9
    assert all(r.decision is Decision.REJECT for r in record.rounds)


def test_reject_all_then_swap_finishes_game() -> None:
    session = start_session()
    reach_endgame(session)
    other = session.game_state.available_briefcases()[0]
    DecideFinalSwap(FakeClock()).execute(session, True)

    result = session.game_record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITH_SWAP
    assert result.amount_received == other.value
    assert result.final_briefcase_number == other.number
    assert result.player_briefcase_value == Money.of(10)
    assert session.game_state.status is GameStatus.FINISHED


def test_endgame_before_final_swap_pending_raises() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    with pytest.raises(InvalidGameStateError):
        DecideFinalSwap(FakeClock()).execute(session, True)
    assert session.game_record.official_result is None


def test_operation_after_finished_raises() -> None:
    session = start_session()
    reach_endgame(session)
    DecideFinalSwap(FakeClock()).execute(session, False)
    # Game is FINISHED: a second endgame decision must be rejected by the domain.
    with pytest.raises(InvalidGameStateError):
        DecideFinalSwap(FakeClock()).execute(session, False)


def test_two_final_briefcases_revealed_not_as_round_openings() -> None:
    session = start_session()
    reach_endgame(session)
    DecideFinalSwap(FakeClock()).execute(session, True)
    record = session.game_record
    total_round_openings = sum(len(r.openings) for r in record.rounds)
    assert total_round_openings == 24
    assert len(session.game_state.opened_briefcases()) == 26
    assert session.game_state.closed_briefcase_count() == 0
