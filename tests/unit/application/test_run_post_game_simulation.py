"""Unit tests for the RunPostGameSimulation use case (Phase 6)."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_offer import DecideOffer
from tont_game.application.use_cases.open_briefcase import OpenBriefcase
from tont_game.application.use_cases.process_banker_offer import ProcessBankerOffer
from tont_game.application.use_cases.run_post_game_simulation import (
    RunPostGameSimulation,
)
from tont_game.application.use_cases.select_initial_briefcase import (
    SelectInitialBriefcase,
)
from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.history.records import Decision
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.simulation.post_game_simulation import (
    SimulationScenario,
    simulate_continue_hold,
)
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")
MOMENT = datetime(2026, 7, 28, 20, 0, tzinfo=UTC)


class FakeClock:
    def now(self) -> datetime:
        return MOMENT


class FakeIdGenerator:
    def new_id(self) -> UUID:
        return uuid4()


class IdentityRandomSource:
    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


def topa_session() -> GameSession:
    values = [Money.of(n) for n in range(1, 27)]
    session = StartGame(FakeClock(), FakeIdGenerator()).execute(
        IdentityRandomSource(), values=values
    )
    SelectInitialBriefcase().execute(session, 10)  # player holds value 10
    state = session.game_state
    for briefcase in state.available_briefcases()[
        : state.openings_required_in_current_round()
    ]:
        OpenBriefcase().execute(session, briefcase.number)
    ProcessBankerOffer(DefaultBankerStrategy()).execute(session)
    DecideOffer(FakeClock()).execute(session, Decision.ACCEPT)
    return session


def test_returns_correct_simulation_result() -> None:
    session = topa_session()
    result = RunPostGameSimulation().execute(session.game_record)
    assert result.scenario is SimulationScenario.CONTINUE_HOLD
    assert result.hypothetical_amount == Money.of(10)  # player briefcase value
    assert result.official_amount == Money.of("5.78")  # accepted offer


def test_delegates_to_the_domain_service() -> None:
    session = topa_session()
    use_case_result = RunPostGameSimulation().execute(session.game_record)
    domain_result = simulate_continue_hold(session.game_record)
    assert use_case_result == domain_result


def test_does_not_mutate_session_state_or_history() -> None:
    session = topa_session()
    status_before = session.game_state.status
    official_before = session.game_record.official_result
    rounds_before = session.game_record.rounds

    RunPostGameSimulation().execute(session.game_record)

    assert session.game_state.status is status_before
    assert session.game_state.status is GameStatus.ACCEPTED
    assert session.game_record.official_result is official_before
    assert session.game_record.rounds == rounds_before
