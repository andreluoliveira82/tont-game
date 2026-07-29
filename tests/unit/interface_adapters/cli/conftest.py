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

from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.interface_adapters.cli.controller import CliController

T = TypeVar("T")


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


def build_controller(console: FakeConsole, *, seed: int | None = None) -> CliController:
    return CliController(
        console=console,
        clock=FakeClock(),
        id_generator=FakeIdGenerator(),
        random_source=IdentityRandomSource(),
        banker_strategy=DefaultBankerStrategy(),
        seed=seed,
    )


@pytest.fixture
def run_cli():
    """Return a function that runs a full CLI game with scripted input."""

    def _run(inputs: Sequence[str], *, seed: int | None = None) -> FakeConsole:
        console = FakeConsole(inputs)
        build_controller(console, seed=seed).run()
        return console

    return _run
