"""Default random source.

Concrete implementation of the domain ``RandomSource`` port backed by
``random.Random``. An optional integer seed makes the shuffling reproducible;
without a seed, ``random.Random`` seeds itself from the OS entropy.

Note: this deliberately uses ``random.Random`` (seedable/reproducible), not
``random.SystemRandom`` (OS entropy, not seedable) — hence the neutral name.
"""

import random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class DefaultRandomSource:
    """A ``RandomSource`` backed by ``random.Random`` with an optional seed."""

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._random = random.Random(seed)

    @property
    def seed(self) -> int | None:
        return self._seed

    def shuffle(self, items: Sequence[T]) -> list[T]:
        result = list(items)
        self._random.shuffle(result)
        return result
