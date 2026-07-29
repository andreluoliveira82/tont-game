"""Command-line entry point (composition root).

Wires the concrete infrastructure adapters and the banker strategy into the CLI
controller and runs a full game. An optional integer seed may be passed as the
first argument (``python -m tont_game 42``) for reproducible games; without it,
the game is random.
"""

import sys

from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.infrastructure.clock import SystemClock
from tont_game.infrastructure.identifiers import UuidGameIdGenerator
from tont_game.infrastructure.randomness.random_source import DefaultRandomSource
from tont_game.interface_adapters.cli.controller import CliController
from tont_game.interface_adapters.cli.views import TerminalConsole


def _parse_seed(args: list[str]) -> int | None:
    if not args:
        return None
    try:
        return int(args[0])
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    seed = _parse_seed(args)
    controller = CliController(
        console=TerminalConsole(),
        clock=SystemClock(),
        id_generator=UuidGameIdGenerator(),
        random_source=DefaultRandomSource(seed),
        banker_strategy=DefaultBankerStrategy(),
        seed=seed,
    )
    controller.run()


if __name__ == "__main__":
    main()
