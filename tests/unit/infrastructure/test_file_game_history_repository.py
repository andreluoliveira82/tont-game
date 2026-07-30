"""Unit tests for the file-based game history repository (Phase 11).

Uses ``tmp_path`` so tests never touch the real user directory.
"""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import OfficialResult
from tont_game.domain.history.repository import GameHistoryError
from tont_game.domain.value_objects.money import Money
from tont_game.infrastructure.persistence.file_game_history_repository import (
    FileGameHistoryRepository,
)


def finished_record(finished_at: datetime, amount: str = "100") -> GameRecord:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("250"))],
    )
    record.record_player_briefcase(1)
    record.close(
        OfficialResult.from_accepted_offer(
            decision_round=1,
            accepted_offer=Money.of(amount),
            player_briefcase_value=Money.of("250"),
        ),
        finished_at,
    )
    return record


def test_save_then_list_returns_the_summary(tmp_path: Path) -> None:
    repository = FileGameHistoryRepository(tmp_path)
    record = finished_record(datetime(2026, 7, 29, 10, tzinfo=UTC), amount="120.50")
    repository.save(record)

    summaries = repository.list_summaries()
    assert len(summaries) == 1
    assert summaries[0].game_id == record.game_id
    assert summaries[0].amount_received == Money.of("120.50")


def test_save_creates_the_directory_if_missing(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "history"
    repository = FileGameHistoryRepository(target)
    repository.save(finished_record(datetime(2026, 7, 29, 10, tzinfo=UTC)))
    assert list(target.glob("*.json"))


def test_list_is_empty_when_directory_absent(tmp_path: Path) -> None:
    repository = FileGameHistoryRepository(tmp_path / "does-not-exist")
    assert repository.list_summaries() == []


def test_corrupted_entry_is_skipped(tmp_path: Path) -> None:
    repository = FileGameHistoryRepository(tmp_path)
    repository.save(finished_record(datetime(2026, 7, 29, 10, tzinfo=UTC)))
    (tmp_path / "broken.json").write_text("{ not valid json", encoding="utf-8")

    summaries = repository.list_summaries()
    assert len(summaries) == 1  # the valid one survives; the broken one is skipped


def test_summaries_are_sorted_most_recent_first(tmp_path: Path) -> None:
    repository = FileGameHistoryRepository(tmp_path)
    older = finished_record(datetime(2026, 7, 29, 8, tzinfo=UTC), amount="10")
    newer = finished_record(datetime(2026, 7, 29, 20, tzinfo=UTC), amount="20")
    repository.save(older)
    repository.save(newer)

    summaries = repository.list_summaries()
    assert [s.amount_received for s in summaries] == [Money.of("20"), Money.of("10")]


def test_save_wraps_io_failure_in_game_history_error(tmp_path: Path) -> None:
    # Point the repository at a path whose parent is a file, so mkdir fails.
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    repository = FileGameHistoryRepository(blocker / "history")
    with pytest.raises(GameHistoryError):
        repository.save(finished_record(datetime(2026, 7, 29, 10, tzinfo=UTC)))
