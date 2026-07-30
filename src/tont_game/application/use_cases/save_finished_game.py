"""SaveFinishedGame: persist a finished game via the history repository.

Thin use case: it requires a finished game (official result present) and
delegates the actual storage to the injected repository port. Graceful
degradation on I/O failure is the caller's responsibility (the repository
raises ``GameHistoryError``).
"""

from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.repository import GameHistoryRepository


class SaveFinishedGame:
    def __init__(self, repository: GameHistoryRepository) -> None:
        self._repository = repository

    def execute(self, record: GameRecord) -> None:
        if record.official_result is None:
            raise InvalidGameStateError("Cannot save a game that has not finished.")
        self._repository.save(record)
