"""File-based ``GameHistoryRepository``: one JSON file per finished game.

The target directory is injected (resolved by ``locations`` in the composition
root), so this adapter never hardcodes a path. I/O failures are wrapped in
``GameHistoryError`` for the caller to handle; individual corrupted files are
skipped when listing so one bad file never hides the rest of the history.
"""

import json
from pathlib import Path

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.repository import (
    GameHistoryError,
    GameHistorySummary,
)
from tont_game.infrastructure.persistence.game_record_schema import (
    serialize,
    summary_from_dict,
)


class FileGameHistoryRepository:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def save(self, record: GameRecord) -> None:
        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(serialize(record), ensure_ascii=False, indent=2)
            (self._directory / self._filename(record)).write_text(
                payload, encoding="utf-8"
            )
        except OSError as error:
            raise GameHistoryError(f"Failed to save game history: {error}") from error

    def list_summaries(self) -> list[GameHistorySummary]:
        try:
            if not self._directory.exists():
                return []
            files = sorted(self._directory.glob("*.json"))
        except OSError as error:
            raise GameHistoryError(f"Failed to access game history: {error}") from error
        summaries = [
            summary
            for path in files
            if (summary := self._read_summary(path)) is not None
        ]
        summaries.sort(key=lambda summary: summary.finished_at, reverse=True)
        return summaries

    @staticmethod
    def _filename(record: GameRecord) -> str:
        moment = record.finished_at or record.started_at
        return f"{moment.strftime('%Y%m%dT%H%M%S')}-{record.game_id}.json"

    @staticmethod
    def _read_summary(path: Path) -> GameHistorySummary | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return summary_from_dict(data)
        except (OSError, ValueError, KeyError):
            return None  # skip a corrupted or unreadable entry
