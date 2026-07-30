"""Shared test doubles for the CLI tests.

``FakeConsole`` scripts the player's input and records everything written, so a
whole game can be driven deterministically. ``build_controller`` wires a
``CliController`` with deterministic test doubles (identity shuffle, so the
official value at position ``i`` lands in briefcase ``i``).
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

import pytest

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.repository import GameHistoryError, GameHistorySummary
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.interface_adapters.cli.controller import CliController
from tont_game.interface_adapters.cli.history_controller import HistoryController

T = TypeVar("T")


class _StubHistoryRepository:
    """Returns a fixed list of summaries (for listing tests)."""

    def __init__(self, summaries: Sequence[GameHistorySummary]) -> None:
        self._summaries = list(summaries)

    def save(self, record: GameRecord) -> None:  # pragma: no cover - unused here
        raise NotImplementedError

    def list_summaries(self) -> list[GameHistorySummary]:
        return list(self._summaries)


class FakeHistoryRepository:
    """In-memory repository double that records what would be persisted."""

    def __init__(self) -> None:
        self.saved: list[GameRecord] = []

    def save(self, record: GameRecord) -> None:
        self.saved.append(record)

    def list_summaries(self) -> list[GameHistorySummary]:
        return []


class FailingHistoryRepository:
    """Repository double that always fails, to exercise graceful degradation."""

    def save(self, record: GameRecord) -> None:
        raise GameHistoryError("boom")

    def list_summaries(self) -> list[GameHistorySummary]:
        raise GameHistoryError("boom")


class FakeConsole:
    def __init__(self, inputs: Sequence[str]) -> None:
        self._inputs = list(inputs)
        self.outputs: list[str] = []

    def write(self, text: str) -> None:
        self.outputs.append(text)

    def read_line(self, prompt: str) -> str:
        self.outputs.append(prompt)
        if not self._inputs:
            raise AssertionError("FakeConsole ran out of scripted input.")
        return self._inputs.pop(0)

    @property
    def text(self) -> str:
        return "\n".join(self.outputs)


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 28, tzinfo=UTC)


class FakeIdGenerator:
    def new_id(self) -> UUID:
        return uuid4()


class IdentityRandomSource:
    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


def build_controller(
    console: FakeConsole,
    *,
    seed: int | None = None,
    history_repository: object | None = None,
) -> CliController:
    return CliController(
        console=console,
        clock=FakeClock(),
        id_generator=FakeIdGenerator(),
        random_source=IdentityRandomSource(),
        banker_strategy=DefaultBankerStrategy(),
        seed=seed,
        history_repository=history_repository,  # type: ignore[arg-type]
    )


@pytest.fixture
def run_cli():
    """Return a function that runs a full CLI game with scripted input."""

    def _run(
        inputs: Sequence[str],
        *,
        seed: int | None = None,
        history_repository: object | None = None,
    ) -> FakeConsole:
        console = FakeConsole(inputs)
        build_controller(
            console, seed=seed, history_repository=history_repository
        ).run()
        return console

    return _run


@pytest.fixture
def make_controller():
    """Return a factory that builds a controller around any console double."""

    def _make(console: object, *, seed: int | None = None) -> CliController:
        return build_controller(console, seed=seed)  # type: ignore[arg-type]

    return _make


@pytest.fixture
def fake_history_repo() -> FakeHistoryRepository:
    """A repository double that records saved games in memory."""
    return FakeHistoryRepository()


@pytest.fixture
def failing_history_repo() -> FailingHistoryRepository:
    """A repository double that always fails, for graceful-degradation tests."""
    return FailingHistoryRepository()


@pytest.fixture
def run_history():
    """Run the history-listing command and return the recording console."""

    def _run(
        summaries: Sequence[GameHistorySummary] = (), *, failing: bool = False
    ) -> FakeConsole:
        console = FakeConsole([])
        repository = (
            FailingHistoryRepository() if failing else _StubHistoryRepository(summaries)
        )
        HistoryController(console, repository).list()  # type: ignore[arg-type]
        return console

    return _run
