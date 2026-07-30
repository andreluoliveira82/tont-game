"""Unit tests for the persistence location resolver (Phase 11)."""

from pathlib import Path

import pytest

from tont_game.infrastructure.persistence import locations


def test_history_directory_lives_under_the_user_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(locations.Path, "home", classmethod(lambda cls: tmp_path))
    assert locations.history_directory() == tmp_path / ".tont-game" / "history"
