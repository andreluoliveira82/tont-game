"""Post-game simulation service.

A pure derivation over an immutable, finished ``GameRecord``. It never mutates
the record, the official result or any other state, and its result is not part
of the history and is not persisted.

Phase 6 scope (MVP): the single scenario ``CONTINUE_HOLD`` — for a game ended by
accepting an offer (Topa), what the player would have received had they refused
the offer and held their own briefcase to the end, compared to the amount they
officially received.
"""

from dataclasses import dataclass
from enum import Enum

from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.value_objects.money import Money


class SimulationScenario(Enum):
    """The hypothetical scenario a simulation represents."""

    CONTINUE_HOLD = "CONTINUE_HOLD"


@dataclass(frozen=True)
class SimulationResult:
    """Immutable, non-historical result of a post-game simulation.

    It is separate from ``OfficialResult``, is not part of the ``GameRecord``
    and is not persisted. Absolute difference and comparison direction are
    derived on demand (see the helpers), never stored.
    """

    scenario: SimulationScenario
    hypothetical_amount: Money
    official_amount: Money

    def absolute_difference(self) -> Money:
        """Derived, non-negative difference between the two amounts."""
        high = max(self.hypothetical_amount.amount, self.official_amount.amount)
        low = min(self.hypothetical_amount.amount, self.official_amount.amount)
        return Money(high - low)

    def hypothetical_is_higher(self) -> bool:
        """Derived: whether the hypothetical amount beats the official one."""
        return self.hypothetical_amount > self.official_amount


def simulate_continue_hold(game_record: GameRecord) -> SimulationResult:
    """Derive the ``CONTINUE_HOLD`` simulation for a finished game.

    Requires a finished game (``official_result`` present); otherwise raises
    ``InvalidGameStateError``.
    """
    official_result = game_record.official_result
    if official_result is None:
        raise InvalidGameStateError(
            "Cannot simulate a game that has no official result."
        )
    return SimulationResult(
        scenario=SimulationScenario.CONTINUE_HOLD,
        hypothetical_amount=official_result.player_briefcase_value,
        official_amount=official_result.amount_received,
    )
