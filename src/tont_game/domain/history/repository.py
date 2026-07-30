"""Outbound port for persisting and retrieving finished games.

Persistence is an **optional capability**: the domain defines this port, but the
game must remain fully playable without any repository. Failures surface as
``GameHistoryError`` (a technical failure, not a domain-rule violation) so that
callers can degrade gracefully.

The concrete storage strategy lives in the infrastructure layer (see ADR 0007).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable
from uuid import UUID

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import EndingType
from tont_game.domain.value_objects.money import Money


class GameHistoryError(Exception):
    """Raised when persisting or reading the game history fails.

    This is a technical (infrastructure) failure exposed through the port, not a
    ``DomainError``: persistence is optional and callers should degrade
    gracefully when it is raised.
    """


@dataclass(frozen=True)
class GameHistorySummary:
    """A lightweight, read-only view of a finished game, for listing."""

    game_id: UUID
    finished_at: datetime
    ending_type: EndingType
    amount_received: Money
    player_briefcase_value: Money


@runtime_checkable
class GameHistoryRepository(Protocol):
    """Port for storing finished games and reading them back."""

    def save(self, record: GameRecord) -> None:
        """Persist a finished game. Raises ``GameHistoryError`` on failure."""
        ...

    def list_summaries(self) -> list[GameHistorySummary]:
        """Return summaries of persisted games, most recent first.

        Unreadable or corrupted individual entries are skipped;
        ``GameHistoryError`` is raised only when the underlying store as a whole
        cannot be accessed.
        """
        ...
