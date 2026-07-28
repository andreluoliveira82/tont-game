"""Integration tests for a full Phase 5 game flow (no CLI, no endgame)."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_offer import DecideOffer
from tont_game.application.use_cases.open_briefcase import OpenBriefcase
from tont_game.application.use_cases.process_banker_offer import ProcessBankerOffer
from tont_game.application.use_cases.select_initial_briefcase import (
    SelectInitialBriefcase,
)
from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.history.records import Decision, EndingType
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")
MOMENT = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)


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
        IdentityRandomSource(), seed=7, values=values
    )


def open_full_round(session: GameSession) -> None:
    state = session.game_state
    to_open = state.openings_required_in_current_round()
    opener = OpenBriefcase()
    for briefcase in state.available_briefcases()[:to_open]:
        opener.execute(session, briefcase.number)


def test_topa_on_first_round_full_flow() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)  # player holds value 10
    open_full_round(session)  # opens values 1..6
    offer = ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.ACCEPT)

    record = session.game_record
    result = record.official_result
    assert result is not None
    assert result.ending_type is EndingType.OFFER_ACCEPTED
    assert result.amount_received == offer == Money.of("5.78")
    assert result.player_briefcase_value == Money.of(10)
    assert result.decision_round == 1
    assert record.finished_at == MOMENT
    assert session.game_state.is_over() is True

    assert len(record.rounds) == 1
    assert len(record.rounds[0].openings) == 6
    assert record.rounds[0].decision is Decision.ACCEPT
    assert record.seed == 7
    assert len(record.initial_distribution) == 26


def test_reject_then_accept_across_rounds() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)

    open_full_round(session)
    ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.REJECT)
    assert session.game_state.current_round == 2

    open_full_round(session)
    ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.ACCEPT)

    record = session.game_record
    assert record.official_result is not None
    assert record.official_result.decision_round == 2
    assert len(record.rounds) == 2
    assert record.rounds[0].decision is Decision.REJECT
    assert record.rounds[1].decision is Decision.ACCEPT


def test_reject_all_reaches_final_swap_pending_without_official_result() -> None:
    session = start_session()
    SelectInitialBriefcase().execute(session, 10)
    strategy = DefaultBankerStrategy()
    clock = FakeClock()

    while session.game_state.status is not GameStatus.FINAL_SWAP_PENDING:
        open_full_round(session)
        ProcessBankerOffer(strategy).execute(session)
        DecideOffer(clock).execute(session, Decision.REJECT)

    record = session.game_record
    assert session.game_state.status is GameStatus.FINAL_SWAP_PENDING
    assert session.game_state.is_over() is False
    # Endgame not implemented in Phase 5: no official result yet.
    assert record.official_result is None
    assert len(record.rounds) == 9
    assert all(r.decision is Decision.REJECT for r in record.rounds)
