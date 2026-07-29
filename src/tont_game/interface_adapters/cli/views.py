"""Views: the I/O boundary of the CLI.

``Console`` is the abstraction the controller depends on, so tests can inject a
scripted double. ``TerminalConsole`` is the concrete terminal implementation.
"""

from typing import Protocol


class Console(Protocol):
    def write(self, text: str) -> None:
        """Write a line of output."""
        ...

    def read_line(self, prompt: str) -> str:
        """Show ``prompt`` and read one line of input."""
        ...


class TerminalConsole:
    """Concrete ``Console`` using the standard input/output."""

    def write(self, text: str) -> None:
        print(text)

    def read_line(self, prompt: str) -> str:
        return input(prompt)
