"""Filesystem locations for persisted data.

Encapsulated in the infrastructure layer on purpose: the rest of the app never
hardcodes a path — it receives a directory from here. Moving to an XDG/AppData
convention (or elsewhere) later touches only this module.
"""

from pathlib import Path


def history_directory() -> Path:
    """Return the directory where finished games are stored."""
    return Path.home() / ".tont-game" / "history"
