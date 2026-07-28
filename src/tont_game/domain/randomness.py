"""Randomness port.

Defines the abstraction the domain depends on to shuffle values. The domain
never imports a concrete randomness implementation (e.g. ``random``); a
concrete source is injected from the outside (infrastructure) and can be
replaced by a deterministic double in tests.
"""

from collections.abc import Sequence
from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class RandomSource(Protocol):
    """An injectable source of randomness used to shuffle sequences."""

    def shuffle(self, items: Sequence[T]) -> list[T]:
        """Return a new list containing ``items`` in a random order."""
        ...
