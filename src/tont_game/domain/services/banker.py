"""Banker strategy: computes the banker's offer.

The strategy is a stateless domain policy. It depends only on the current
remaining values (``Money`` value objects) and the current round number; it
has no knowledge of ``GameState``, of previous offers, of the CLI or of
infrastructure.

No artificial monotonicity is applied: the offer follows purely from the
received state and round. Because the composition of the remaining values
changes as briefcases are opened, the offer may rise, fall or stay close to
the previous one — this is intentional (see docs/game-rules.md, section 7, and
docs/decisions/0002-estrategia-inicial-do-banqueiro.md).
"""

from collections.abc import Sequence
from decimal import Decimal
from typing import Protocol, runtime_checkable

from tont_game.domain.errors import BankerStrategyError
from tont_game.domain.value_objects.money import Money

DEFAULT_BANKER_PERCENTAGES: tuple[Decimal, ...] = (
    Decimal("0.35"),  # round 1
    Decimal("0.40"),  # round 2
    Decimal("0.50"),  # round 3
    Decimal("0.60"),  # round 4
    Decimal("0.70"),  # round 5
    Decimal("0.80"),  # round 6
    Decimal("0.85"),  # round 7
    Decimal("0.90"),  # round 8
    Decimal("0.95"),  # round 9
)


@runtime_checkable
class BankerStrategy(Protocol):
    """Port for a banker offer policy. Implementations must be substitutable."""

    def offer(self, remaining_values: Sequence[Money], round_number: int) -> Money:
        """Return the banker's offer for the given remaining values and round."""
        ...

    def percentage_for_round(self, round_number: int) -> Decimal:
        """Return the percentage the policy applies in the given round.

        Reported for auditing (recorded in the game history), independently of
        being derivable from the offer.
        """
        ...


class DefaultBankerStrategy:
    """Initial banker policy: mean of remaining values times a round percentage.

    ``offer = mean(remaining_values) * percentage(round_number)``, rounded to
    cents only at the end. Stateless and history-free.
    """

    def __init__(
        self, percentages: Sequence[Decimal] = DEFAULT_BANKER_PERCENTAGES
    ) -> None:
        self._percentages = tuple(percentages)
        self._validate_percentages(self._percentages)

    def offer(self, remaining_values: Sequence[Money], round_number: int) -> Money:
        if not remaining_values:
            raise BankerStrategyError(
                "Cannot compute an offer with no remaining values."
            )
        percentage = self.percentage_for_round(round_number)
        total = sum((value.amount for value in remaining_values), Decimal(0))
        mean = total / Decimal(len(remaining_values))
        return Money.of(mean * percentage)

    def percentage_for_round(self, round_number: int) -> Decimal:
        if not 1 <= round_number <= len(self._percentages):
            raise BankerStrategyError(
                f"Round {round_number} has no configured percentage."
            )
        return self._percentages[round_number - 1]

    @staticmethod
    def _validate_percentages(percentages: tuple[Decimal, ...]) -> None:
        if not percentages:
            raise BankerStrategyError("At least one round percentage is required.")
        for percentage in percentages:
            if not isinstance(percentage, Decimal):
                raise BankerStrategyError("Percentages must be Decimal values.")
            if percentage < 0 or percentage > 1:
                raise BankerStrategyError("Percentages must be between 0 and 1.")
