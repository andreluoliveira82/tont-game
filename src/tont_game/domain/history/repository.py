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
from tont_game.domain.history.records import Decision, EndingType
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


@dataclass(frozen=True)
class GameHistoryRoundDetail:
    """Read-only detail of a single round within a persisted game."""

    round_number: int
    openings: tuple[tuple[int, Money], ...]
    offer: Money | None
    decision: Decision | None


@dataclass(frozen=True)
class GameHistoryDetail:
    """Read-only detail of a single persisted game (for ``history show``)."""

    game_id: UUID
    started_at: datetime
    finished_at: datetime | None
    seed: int | None
    player_briefcase: int | None
    ending_type: EndingType
    amount_received: Money
    player_briefcase_value: Money
    rounds: tuple[GameHistoryRoundDetail, ...]


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

    def get(self, game_id: UUID) -> GameHistoryDetail | None:
        """Return the detail of a persisted game, or ``None`` if it is not
        found or cannot be read (e.g. corrupted or an unknown schema version).

        ``GameHistoryError`` is raised only when the underlying store as a whole
        cannot be accessed.
        """
        ...
