"""Command-line entry point (composition root).

Wires the concrete infrastructure adapters, the banker strategy and the game
history repository into the CLI. It dispatches on the first argument:

- ``python -m tont_game``            → play a random game
- ``python -m tont_game 42``         → play a reproducible game (seed 42)
- ``python -m tont_game history``    → list past games

The dispatch is organized so future history subcommands (``show``, ``stats``,
``export``) can be added without breaking the existing commands.
"""

import sys

from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.infrastructure.clock import SystemClock
from tont_game.infrastructure.identifiers import UuidGameIdGenerator
from tont_game.infrastructure.persistence.file_game_history_repository import (
    FileGameHistoryRepository,
)
from tont_game.infrastructure.persistence.locations import history_directory
from tont_game.infrastructure.randomness.random_source import DefaultRandomSource
from tont_game.interface_adapters.cli import presenters
from tont_game.interface_adapters.cli.controller import CliController
from tont_game.interface_adapters.cli.history_controller import HistoryController
from tont_game.interface_adapters.cli.views import Console, TerminalConsole


def _parse_seed(args: list[str]) -> int | None:
    if not args:
        return None
    try:
        return int(args[0])
    except ValueError:
        return None


def _select_command(args: list[str]) -> str:
    if args and args[0] == "history":
        return "history"
    return "play"


def _run_history(
    args: list[str], console: Console, repository: FileGameHistoryRepository
) -> None:
    controller = HistoryController(console, repository)
    subcommand = args[1] if len(args) > 1 else None
    if subcommand is None:
        controller.list()
    elif subcommand == "show":
        if len(args) > 2:
            controller.show(args[2])
        else:
            console.write(presenters.history_show_usage())
    else:
        console.write(presenters.history_unknown_subcommand(subcommand))


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    console = TerminalConsole()
    repository = FileGameHistoryRepository(history_directory())

    if _select_command(args) == "history":
        _run_history(args, console, repository)
        return

    seed = _parse_seed(args)
    controller = CliController(
        console=console,
        clock=SystemClock(),
        id_generator=UuidGameIdGenerator(),
        random_source=DefaultRandomSource(seed),
        banker_strategy=DefaultBankerStrategy(),
        seed=seed,
        history_repository=repository,
    )
    controller.run()


if __name__ == "__main__":
    main()
