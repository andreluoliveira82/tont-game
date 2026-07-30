"""GetGameHistoryDetail: retrieve the full detail of one persisted game."""

from uuid import UUID

from tont_game.domain.history.repository import (
    GameHistoryDetail,
    GameHistoryRepository,
)


class GetGameHistoryDetail:
    def __init__(self, repository: GameHistoryRepository) -> None:
        self._repository = repository

    def execute(self, game_id: UUID) -> GameHistoryDetail | None:
        return self._repository.get(game_id)
