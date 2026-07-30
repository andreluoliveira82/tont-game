"""ListGameHistory: retrieve summaries of previously persisted games."""

from tont_game.domain.history.repository import (
    GameHistoryRepository,
    GameHistorySummary,
)


class ListGameHistory:
    def __init__(self, repository: GameHistoryRepository) -> None:
        self._repository = repository

    def execute(self) -> list[GameHistorySummary]:
        return self._repository.list_summaries()
