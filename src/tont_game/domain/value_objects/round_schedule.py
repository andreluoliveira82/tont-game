"""Round structure of a game.

Represents how many briefcases must be opened in each round. The default
schedule is the official 9-round sequence documented in docs/game-rules.md
and docs/decisions/0001-estrutura-rodadas-e-endgame.md:

    round 1 -> 6, round 2 -> 5, round 3 -> 4, round 4 -> 3, round 5 -> 2,
    rounds 6..9 -> 1 each  (total: 24 openings)
"""

from dataclasses import dataclass

DEFAULT_ROUND_OPENINGS: tuple[int, ...] = (6, 5, 4, 3, 2, 1, 1, 1, 1)


@dataclass(frozen=True)
class RoundSchedule:
    """Immutable per-round opening counts."""

    openings: tuple[int, ...] = DEFAULT_ROUND_OPENINGS

    def __post_init__(self) -> None:
        if not self.openings:
            raise ValueError("A round schedule must have at least one round.")
        if any(count <= 0 for count in self.openings):
            raise ValueError("Every round must open at least one briefcase.")

    @property
    def total_rounds(self) -> int:
        return len(self.openings)

    @property
    def total_openings(self) -> int:
        return sum(self.openings)

    def has_round(self, round_number: int) -> bool:
        return 1 <= round_number <= self.total_rounds

    def openings_for_round(self, round_number: int) -> int:
        if not self.has_round(round_number):
            raise ValueError(f"Round {round_number} is out of range.")
        return self.openings[round_number - 1]
