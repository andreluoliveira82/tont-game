"""Clock port.

Abstraction the domain/application depend on to obtain the current time. A
concrete clock is injected from the outside (infrastructure) and can be
replaced by a deterministic double in tests. Timestamps are timezone-aware
and expressed in UTC; formatting/localization belong to outer layers.
"""

from datetime import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """A source of the current time (timezone-aware, UTC)."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware datetime in UTC."""
        ...
