"""Briefcase entity.

A briefcase is identified by its number and holds a fixed monetary value.
Its only mutable state is whether it has been opened. Once opened it can
never become closed again.
"""

from dataclasses import dataclass

from tont_game.domain.errors import BriefcaseAlreadyOpenedError
from tont_game.domain.value_objects.money import Money


@dataclass
class Briefcase:
    number: int
    value: Money
    opened: bool = False

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError("Briefcase number must be a positive integer.")
        if not isinstance(self.value, Money):
            raise TypeError("Briefcase value must be a Money instance.")

    def open(self) -> None:
        """Reveal the briefcase. Raises if it is already opened."""
        if self.opened:
            raise BriefcaseAlreadyOpenedError(
                f"Briefcase {self.number} is already opened."
            )
        self.opened = True
