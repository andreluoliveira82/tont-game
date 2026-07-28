"""Lifecycle status of a game.

The full documented set of statuses is defined here (see docs/glossary.md).
Only ``NOT_STARTED`` and ``IN_PROGRESS`` are reachable within the Phase 2
domain model; the remaining statuses become reachable once offers, the
endgame and the official result are implemented in later phases.
"""

from enum import Enum


class GameStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    OFFER_PENDING = "OFFER_PENDING"
    ACCEPTED = "ACCEPTED"
    FINAL_SWAP_PENDING = "FINAL_SWAP_PENDING"
    FINAL_REVEAL = "FINAL_REVEAL"
    FINISHED = "FINISHED"
