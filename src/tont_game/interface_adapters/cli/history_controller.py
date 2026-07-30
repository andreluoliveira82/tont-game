"""CLI controller for the ``history`` command group.

Kept separate from the game loop (SRP) and organized so future subcommands
(``history show``, ``history stats``, ``history export``) can be added without
breaking compatibility. Reading failures degrade gracefully.
"""

from uuid import UUID

from tont_game.application.use_cases.get_game_history_detail import (
    GetGameHistoryDetail,
)
from tont_game.application.use_cases.list_game_history import ListGameHistory
from tont_game.domain.history.repository import (
    GameHistoryError,
    GameHistoryRepository,
)
from tont_game.interface_adapters.cli import presenters
from tont_game.interface_adapters.cli.views import Console


class HistoryController:
    def __init__(self, console: Console, repository: GameHistoryRepository) -> None:
        self._console = console
        self._repository = repository

    def list(self) -> None:
        try:
            summaries = ListGameHistory(self._repository).execute()
        except GameHistoryError:
            self._console.write(presenters.history_unavailable())
            return
        if not summaries:
            self._console.write(presenters.history_empty())
            return
        self._console.write(presenters.history_list(summaries))

    def show(self, raw_id: str) -> None:
        try:
            game_id = UUID(raw_id)
        except ValueError:
            self._console.write(presenters.history_invalid_id(raw_id))
            return
        try:
            detail = GetGameHistoryDetail(self._repository).execute(game_id)
        except GameHistoryError:
            self._console.write(presenters.history_unavailable())
            return
        if detail is None:
            self._console.write(presenters.history_not_found())
            return
        self._console.write(presenters.history_detail(detail))
