"""GameSession: operational composition of a match.

Bundles the mutable operational state and the factual history. The record
never references the mutable state; both are coordinated by the use cases.
"""

from dataclasses import dataclass

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.history.game_record import GameRecord


@dataclass(frozen=True)
class GameSession:
    game_state: GameState
    game_record: GameRecord
