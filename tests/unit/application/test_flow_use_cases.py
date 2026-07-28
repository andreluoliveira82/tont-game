"""Unit tests for the Phase 5 flow use cases and state/history consistency."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

import pytest

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_offer import DecideOffer
from tont_game.application.use_cases.open_briefcase import OpenBriefcase
from tont_game.application.use_cases.process_banker_offer import ProcessBankerOffer
from tont_game.application.use_cases.select_initial_briefcase import (
    SelectInitialBriefcase,
)
from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.errors import InvalidGameStateError, NoPendingOfferError
from tont_game.domain.history.records import Decision
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")
MOMENT = datetime(2026, 7, 28, tzinfo=UTC)


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
    values = [Money.of(n) for n in range(1, 27)]  # briefcase i holds value i
    return StartGame(FakeClock(), FakeIdGenerator()).execute(
        IdentityRandomSource(), values=values
    )


def open_full_round(session: GameSession) -> None:
    state = session.game_state
    to_open = state.openings_required_in_current_round()
    opener = OpenBriefcase()
    for briefcase in state.available_briefcases()[:to_open]:
        opener.execute(session, briefcase.number)


def test_select_initial_briefcase_updates_state_and_record() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    assert session.game_state.player_briefcase is not None
    assert session.game_state.player_briefcase.number == 10
    assert session.game_record.player_briefcase_number == 10


def test_open_briefcase_records_the_opening() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    OpenBriefcase().execute(session, 1)
    round_record = session.game_record.rounds[0]
    assert round_record.round_number == 1
    assert round_record.openings[0].briefcase_number == 1
    assert round_record.openings[0].value == Money.of(1)


def test_process_offer_sets_pending_and_records_offer() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    open_full_round(session)
    offer = ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    # remaining after opening 1..6: mean 16.5 * 0.35 = 5.775 -> 5.78
    assert offer == Money.of("5.78")
    assert session.game_state.status is GameStatus.OFFER_PENDING
    offer_record = session.game_record.rounds[0].offer
    assert offer_record is not None
    assert offer_record.offer == Money.of("5.78")
    assert offer_record.percentage == DefaultBankerStrategy().percentage_for_round(1)


def test_invalid_offer_does_not_create_a_phantom_fact() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    # Round not complete yet -> the domain refuses the offer...
    with pytest.raises(InvalidGameStateError):
        ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    # ...and no offer was recorded (no phantom fact); state unchanged.
    assert session.game_state.status is GameStatus.IN_PROGRESS
    assert session.game_record.rounds == ()


def test_decide_without_pending_offer_creates_no_fact() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    open_full_round(session)  # round complete, but no offer was processed
    with pytest.raises(NoPendingOfferError):
        DecideOffer(FakeClock()).execute(session, Decision.ACCEPT)
    assert session.game_record.official_result is None
    assert session.game_record.rounds[0].decision is None


def test_initial_distribution_is_independent_of_state_mutation() -> None:
    session = start_session()
    before = session.game_record.initial_distribution
    SelectInitialBriefcase().execute(session, 10)
    open_full_round(session)  # mutates the GameState (opens briefcases)
    after = session.game_record.initial_distribution
    assert before == after
    assert after == tuple((n, Money.of(n)) for n in range(1, 27))


def test_reject_records_decision_and_advances() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    open_full_round(session)
    ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.REJECT)
    assert session.game_record.rounds[0].decision is Decision.REJECT
    assert session.game_state.status is GameStatus.IN_PROGRESS
    assert session.game_state.current_round == 2


def test_accept_records_official_result() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    open_full_round(session)
    offer = ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.ACCEPT)
    result = session.game_record.official_result
    assert result is not None
    assert result.amount_received == offer
    assert result.player_briefcase_value == Money.of(10)
    assert session.game_state.is_over() is True
    assert session.game_record.finished_at == MOMENT
