"""Unit tests for the DecideFinalSwap endgame use case."""

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
MOMENT = datetime(2026, 7, 28, 15, 0, tzinfo=UTC)


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
        IdentityRandomSource(), values=values
    )


def open_full_round(session: GameSession) -> None:
    state = session.game_state
    to_open = state.openings_required_in_current_round()
    opener = OpenBriefcase()
    for briefcase in state.available_briefcases()[:to_open]:
        opener.execute(session, briefcase.number)


def reach_endgame(session: GameSession) -> None:
    SelectInitialBriefcase().execute(session, 10)  # player holds value 10
    strategy = DefaultBankerStrategy()
    clock = FakeClock()
    while session.game_state.status is not GameStatus.FINAL_SWAP_PENDING:
        open_full_round(session)
        ProcessBankerOffer(strategy).execute(session)
        DecideOffer(clock).execute(session, Decision.REJECT)


def test_decide_without_swap_produces_without_swap_result() -> None:
    session = start_session()
    reach_endgame(session)
    DecideFinalSwap(FakeClock()).execute(session, False)

    result = session.game_record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITHOUT_SWAP
    assert result.swap_decision is False
    assert result.amount_received == Money.of(10)
    assert result.player_briefcase_value == Money.of(10)
    assert result.final_briefcase_number == 10
    assert result.decision_round is None
    assert session.game_state.status is GameStatus.FINISHED
    assert session.game_record.finished_at == MOMENT


def test_decide_with_swap_produces_with_swap_result() -> None:
    session = start_session()
    reach_endgame(session)
    other = session.game_state.available_briefcases()[0]

    DecideFinalSwap(FakeClock()).execute(session, True)

    result = session.game_record.official_result
    assert result is not None
    assert result.ending_type is EndingType.FINAL_REVEAL_WITH_SWAP
    assert result.swap_decision is True
    assert result.amount_received == other.value
    assert result.final_briefcase_number == other.number
    assert result.final_briefcase_value == other.value
    assert result.player_briefcase_value == Money.of(10)
    assert result.decision_round is None
    assert session.game_state.status is GameStatus.FINISHED


def test_invalid_state_creates_no_official_result() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)  # IN_PROGRESS, not endgame
    with pytest.raises(InvalidGameStateError):
        DecideFinalSwap(FakeClock()).execute(session, False)
    assert session.game_record.official_result is None
    assert session.game_state.status is GameStatus.IN_PROGRESS


def test_final_reveals_are_not_recorded_as_round_openings() -> None:
    session = start_session()
    reach_endgame(session)
    DecideFinalSwap(FakeClock()).execute(session, False)
    total_openings = sum(len(r.openings) for r in session.game_record.rounds)
    assert total_openings == 24  # the two final reveals are not round openings
    assert len(session.game_state.opened_briefcases()) == 26
