"""RunPostGameSimulation: thin use case delegating to the domain simulation.

It receives an immutable, finished ``GameRecord`` and returns a
``SimulationResult``. It does not receive or mutate the ``GameState`` /
``GameSession``, and it does not persist anything.
"""

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.simulation.post_game_simulation import (
    SimulationResult,
    simulate_continue_hold,
)


class RunPostGameSimulation:
    def execute(self, game_record: GameRecord) -> SimulationResult:
        return simulate_continue_hold(game_record)
