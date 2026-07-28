"""Official briefcase values for the initial version.

This is a product decision (see docs/game-rules.md, section 2) and is meant
to be configurable. It is kept in the domain as the default configuration;
alternative value tables would be a documented decision.
"""

from tont_game.domain.value_objects.money import Money

_OFFICIAL_AMOUNTS: tuple[str, ...] = (
    "0.50",
    "1.00",
    "5.00",
    "10.00",
    "25.00",
    "50.00",
    "75.00",
    "100.00",
    "250.00",
    "500.00",
    "750.00",
    "1000.00",
    "2500.00",
    "5000.00",
    "7500.00",
    "10000.00",
    "25000.00",
    "50000.00",
    "75000.00",
    "100000.00",
    "250000.00",
    "500000.00",
    "750000.00",
    "1000000.00",
    "1500000.00",
    "2000000.00",
)

OFFICIAL_BRIEFCASE_VALUES: tuple[Money, ...] = tuple(
    Money.of(amount) for amount in _OFFICIAL_AMOUNTS
)
