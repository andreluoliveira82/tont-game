"""Game identifier port.

Abstraction for generating the unique identifier of a game. A concrete
generator is injected from the outside (infrastructure) and can be replaced
by a deterministic double in tests.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class GameIdGenerator(Protocol):
    """Generates unique game identifiers."""

    def new_id(self) -> UUID:
        """Return a new unique game identifier."""
        ...
