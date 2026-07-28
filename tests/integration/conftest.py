"""Shared fixtures and a thin game driver for the integration test suite.

The ``GameDriver`` is a test-only convenience that wraps the *real* Application
use cases (it does not reimplement any game logic). Each method maps to one use
case, so integration tests still document the flow step by step while avoiding
boilerplate. Nothing here lives in ``src/`` or acts as a production abstraction.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID

import pytest

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_final_swap import DecideFinalSwap
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
from tont_game.domain.entities.briefcase import Briefcase
from tont_game.domain.entities.game_state import GameState
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import Decision
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.simulation.post_game_simulation import SimulationResult
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")

MOMENT = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)
GAME_ID = UUID("00000000-0000-0000-0000-000000000001")
# Deterministic distribution: with the identity source, briefcase i holds R$ i.
ASCENDING_VALUES: tuple[Money, ...] = tuple(Money.of(n) for n in range(1, 27))


class FakeClock:
    def now(self) -> datetime:
        return MOMENT


class FakeIdGenerator:
    def __init__(self, game_id: UUID = GAME_ID) -> None:
        self._id = game_id

    def new_id(self) -> UUID:
        return self._id


class IdentityRandomSource:
    """Deterministic 'shuffle' that preserves the given order."""

    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


class GameDriver:
    """Drives a game through the real use cases (test-only convenience)."""

    def __init__(
        self, *, seed: int = 7, values: Sequence[Money] = ASCENDING_VALUES
    ) -> None:
        self._clock = FakeClock()
        self._strategy = DefaultBankerStrategy()
        self.session: GameSession = StartGame(self._clock, FakeIdGenerator()).execute(
            IdentityRandomSource(), seed=seed, values=list(values)
        )

    @property
    def state(self) -> GameState:
        return self.session.game_state

    @property
    def record(self) -> GameRecord:
        return self.session.game_record

    # --- flow steps (each wraps a single real use case) ----------------------

    def select(self, number: int) -> None:
        SelectInitialBriefcase().execute(self.session, number)

    def open_briefcase(self, number: int) -> Briefcase:
        return OpenBriefcase().execute(self.session, number)

    def open_full_round(self) -> list[Briefcase]:
        to_open = self.state.openings_required_in_current_round()
        return [
            self.open_briefcase(briefcase.number)
            for briefcase in self.state.available_briefcases()[:to_open]
        ]

    def make_offer(self) -> Money:
        return ProcessBankerOffer(self._strategy).execute(self.session)

    def decide(self, decision: Decision) -> None:
        DecideOffer(self._clock).execute(self.session, decision)

    def decide_final_swap(self, swap: bool) -> None:
        DecideFinalSwap(self._clock).execute(self.session, swap)

    def simulate(self) -> SimulationResult:
        return RunPostGameSimulation().execute(self.record)

    # --- composite helper ----------------------------------------------------

    def reject_until_endgame(self, player: int = 10) -> None:
        """Select the player and reject every offer up to FINAL_SWAP_PENDING."""
        self.select(player)
        while self.state.status is not GameStatus.FINAL_SWAP_PENDING:
            self.open_full_round()
            self.make_offer()
            self.decide(Decision.REJECT)


@pytest.fixture
def moment() -> datetime:
    return MOMENT


@pytest.fixture
def make_driver():
    def _factory(**kwargs: object) -> GameDriver:
        return GameDriver(**kwargs)  # type: ignore[arg-type]

    return _factory


@pytest.fixture
def driver() -> GameDriver:
    return GameDriver()
