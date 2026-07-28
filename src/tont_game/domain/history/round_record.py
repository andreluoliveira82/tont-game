"""RoundRecord: immutable record of the facts of a single round.

A round record is a frozen snapshot. It grows only through the ``with_*``
methods, which return a new instance (the offer and the decision can be set at
most once). Because instances are immutable, a round handed out by the
``GameRecord`` cannot be altered retroactively; only the ``GameRecord`` — the
append-only authority — replaces its own internal entry.
"""

from dataclasses import dataclass, replace

from tont_game.domain.errors import HistoryError
from tont_game.domain.history.records import (
    BankerOfferRecord,
    BriefcaseOpeningRecord,
    Decision,
)


@dataclass(frozen=True)
class RoundRecord:
    round_number: int
    openings: tuple[BriefcaseOpeningRecord, ...] = ()
    offer: BankerOfferRecord | None = None
    decision: Decision | None = None

    def with_opening(self, opening: BriefcaseOpeningRecord) -> "RoundRecord":
        return replace(self, openings=(*self.openings, opening))

    def with_offer(self, offer: BankerOfferRecord) -> "RoundRecord":
        if self.offer is not None:
            raise HistoryError(
                f"Round {self.round_number} already has a recorded offer."
            )
        return replace(self, offer=offer)

    def with_decision(self, decision: Decision) -> "RoundRecord":
        if self.decision is not None:
            raise HistoryError(
                f"Round {self.round_number} already has a recorded decision."
            )
        return replace(self, decision=decision)
