"""Session service: the web adapter's step-wise game orchestrator.

Holds one game session per player in memory (a single game per session; not
persisted, may not survive a restart) and advances it one step per action by
calling the existing use cases. No business rules live here.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

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
from tont_game.domain.clock import Clock
from tont_game.domain.errors import DomainError
from tont_game.domain.history.records import Decision
from tont_game.domain.identifiers import GameIdGenerator
from tont_game.domain.randomness import RandomSource
from tont_game.domain.services.banker import BankerStrategy
from tont_game.domain.simulation.post_game_simulation import SimulationResult
from tont_game.interface_adapters.web.views import game_view


@dataclass
class _Entry:
    session: GameSession
    simulation: SimulationResult | None = None


class UnknownSessionError(Exception):
    """Raised when acting on a session id that does not exist."""


class SessionService:
    def __init__(
        self,
        clock: Clock,
        id_generator: GameIdGenerator,
        banker_strategy: BankerStrategy,
        make_random_source: Callable[[int | None], RandomSource],
    ) -> None:
        self._clock = clock
        self._id_generator = id_generator
        self._strategy = banker_strategy
        self._make_random_source = make_random_source
        self._sessions: dict[str, _Entry] = {}

    def start(self, seed: int | None = None) -> tuple[str, dict[str, Any]]:
        random_source = self._make_random_source(seed)
        session = StartGame(self._clock, self._id_generator).execute(
            random_source, seed=seed
        )
        session_id = str(uuid4())
        self._sessions[session_id] = _Entry(session=session)
        return session_id, game_view(session)

    def act(
        self, session_id: str, action: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        entry = self._sessions.get(session_id)
        if entry is None:
            raise UnknownSessionError(session_id)
        try:
            self._apply(entry, action, params or {})
        except DomainError as error:
            view = game_view(entry.session, entry.simulation)
            view["error"] = str(error)
            return view
        return game_view(entry.session, entry.simulation)

    def _apply(self, entry: _Entry, action: str, params: dict[str, Any]) -> None:
        session = entry.session
        if action == "select_briefcase":
            SelectInitialBriefcase().execute(session, int(params["number"]))
        elif action == "open_briefcase":
            OpenBriefcase().execute(session, int(params["number"]))
            if session.game_state.is_current_round_complete():
                ProcessBankerOffer(self._strategy).execute(session)
        elif action == "decide":
            decision = Decision.ACCEPT if params["accept"] else Decision.REJECT
            DecideOffer(self._clock).execute(session, decision)
        elif action == "decide_swap":
            DecideFinalSwap(self._clock).execute(session, bool(params["swap"]))
        elif action == "simulate":
            entry.simulation = RunPostGameSimulation().execute(session.game_record)
        else:
            raise ValueError(f"Unknown action: {action}")
