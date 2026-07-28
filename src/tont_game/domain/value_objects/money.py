"""Monetary value object with exact decimal precision.

Money is stored as a ``Decimal`` quantized to two decimal places (cents).
Floats are rejected on purpose: they cannot represent money exactly.
PT-BR formatting (e.g. ``R$ 1.000,00``) is a presentation concern and does
not belong here.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

_CENTS = Decimal("0.01")


@dataclass(frozen=True, order=True)
class Money:
    """An immutable, non-negative monetary amount with cent precision."""

    amount: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money.amount must be a Decimal.")
        if self.amount.is_nan() or self.amount.is_infinite():
            raise ValueError("Money.amount must be a finite number.")
        if self.amount < 0:
            raise ValueError("Money cannot be negative.")
        object.__setattr__(
            self, "amount", self.amount.quantize(_CENTS, rounding=ROUND_HALF_UP)
        )

    @classmethod
    def of(cls, value: Decimal | int | str) -> "Money":
        """Build Money from a Decimal, int or str. Floats are not allowed."""
        if isinstance(value, bool):
            raise TypeError("Money cannot be built from a bool.")
        if isinstance(value, float):
            raise TypeError("Money cannot be built from a float; use Decimal/int/str.")
        if isinstance(value, int | str):
            value = Decimal(value)
        return cls(value)

    def __str__(self) -> str:
        return str(self.amount)
