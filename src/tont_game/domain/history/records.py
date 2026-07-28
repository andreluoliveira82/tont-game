"""Immutable historical facts of a game.

These are the leaf records of the history: once created they never change
(``frozen`` dataclasses). Containers (RoundRecord, GameRecord) accumulate them
append-only.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from tont_game.domain.value_objects.money import Money


class Decision(Enum):
    """The player's decision facing an offer."""

    ACCEPT = "ACCEPT"  # Topa
    REJECT = "REJECT"  # Não Topa


class EndingType(Enum):
    """How a game ended officially."""

    OFFER_ACCEPTED = "OFFER_ACCEPTED"
    FINAL_REVEAL_WITH_SWAP = "FINAL_REVEAL_WITH_SWAP"
    FINAL_REVEAL_WITHOUT_SWAP = "FINAL_REVEAL_WITHOUT_SWAP"


@dataclass(frozen=True)
class BriefcaseOpeningRecord:
    """A briefcase revealed during a round."""

    briefcase_number: int
    value: Money


@dataclass(frozen=True)
class BankerOfferRecord:
    """A banker offer, with the facts needed to audit its calculation."""

    round_number: int
    offer: Money
    percentage: Decimal
    remaining_values: tuple[Money, ...]


@dataclass(frozen=True)
class OfficialResult:
    """The official, immutable result of a game.

    ``amount_received`` is what the player officially takes home;
    ``player_briefcase_value`` is the real value of the player's briefcase
    (recorded for audit/simulation even when the player accepts an offer). The
    endgame fields (swap/final briefcase) are reserved for a later phase.
    """

    ending_type: EndingType
    amount_received: Money
    player_briefcase_value: Money
    accepted_offer: Money | None = None
    decision_round: int | None = None
    swap_decision: bool | None = None
    final_briefcase_number: int | None = None
    final_briefcase_value: Money | None = None

    @classmethod
    def from_accepted_offer(
        cls,
        decision_round: int,
        accepted_offer: Money,
        player_briefcase_value: Money,
    ) -> "OfficialResult":
        """Build the official result for an accepted offer (Topa)."""
        return cls(
            ending_type=EndingType.OFFER_ACCEPTED,
            amount_received=accepted_offer,
            player_briefcase_value=player_briefcase_value,
            accepted_offer=accepted_offer,
            decision_round=decision_round,
        )
