"""Value distribution: shuffle values and build the initial game.

This service turns the official (ordered) values into a concrete random
distribution across the 26 briefcases, respecting the domain invariants.
It depends only on the ``RandomSource`` port, never on a concrete randomness
implementation.

The resulting ``GameState`` already holds the concrete distribution of the
match (each briefcase with its value), which is the historical fact of that
execution. Reproducing the same distribution from a seed is a separate,
optional concern handled by the concrete random source.
"""

from collections.abc import Iterable

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.randomness import RandomSource
from tont_game.domain.value_objects.money import Money
from tont_game.domain.value_objects.round_schedule import RoundSchedule


def create_shuffled_game(
    random_source: RandomSource,
    values: Iterable[Money] = OFFICIAL_BRIEFCASE_VALUES,
    schedule: RoundSchedule | None = None,
) -> GameState:
    """Shuffle ``values`` with ``random_source`` and build a ``GameState``.

    Briefcases are numbered ``1..N`` in the shuffled order.
    """
    shuffled = random_source.shuffle(list(values))
    return GameState.create(shuffled, schedule)
