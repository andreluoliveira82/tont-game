"""Public, versioned JSON schema for a persisted game (see ADR 0007).

This module is the **contract** between stored files and the rest of the code.
It maps a ``GameRecord`` to a plain, explicit dictionary (never a naive dump of
Python objects) and reads a lightweight summary back. Money is stored as a
decimal string, timestamps as ISO-8601, identifiers as strings and enums by
their value, so a file stays readable and interpretable even if the internal
domain classes change.

Bump ``SCHEMA_VERSION`` whenever the on-disk shape changes in a
non-backward-compatible way.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import EndingType, OfficialResult
from tont_game.domain.history.repository import GameHistorySummary
from tont_game.domain.history.round_record import RoundRecord
from tont_game.domain.value_objects.money import Money

SCHEMA_VERSION = 1


def serialize(record: GameRecord) -> dict[str, Any]:
    """Map a finished ``GameRecord`` to the public JSON-ready dictionary."""
    return {
        "schema_version": SCHEMA_VERSION,
        "game_id": str(record.game_id),
        "started_at": record.started_at.isoformat(),
        "finished_at": (record.finished_at.isoformat() if record.finished_at else None),
        "seed": record.seed,
        "player_briefcase": record.player_briefcase_number,
        "initial_distribution": [
            {"briefcase": number, "value": _money(value)}
            for number, value in record.initial_distribution
        ],
        "rounds": [_round(round_record) for round_record in record.rounds],
        "official_result": (
            _result(record.official_result) if record.official_result else None
        ),
    }


def summary_from_dict(data: dict[str, Any]) -> GameHistorySummary:
    """Read the lightweight summary fields from a stored dictionary.

    Raises ``KeyError``/``ValueError`` on malformed data; callers decide how to
    handle a corrupted entry.
    """
    result = data["official_result"]
    return GameHistorySummary(
        game_id=UUID(data["game_id"]),
        finished_at=datetime.fromisoformat(data["finished_at"]),
        ending_type=EndingType(result["ending_type"]),
        amount_received=Money.of(result["amount_received"]),
        player_briefcase_value=Money.of(result["player_briefcase_value"]),
    )


def _money(value: Money) -> str:
    return str(value.amount)


def _round(round_record: RoundRecord) -> dict[str, Any]:
    offer = round_record.offer
    return {
        "round": round_record.round_number,
        "openings": [
            {"briefcase": opening.briefcase_number, "value": _money(opening.value)}
            for opening in round_record.openings
        ],
        "offer": (
            {
                "value": _money(offer.offer),
                "percentage": str(offer.percentage),
                "remaining_values": [_money(value) for value in offer.remaining_values],
            }
            if offer
            else None
        ),
        "decision": round_record.decision.value if round_record.decision else None,
    }


def _result(result: OfficialResult) -> dict[str, Any]:
    return {
        "ending_type": result.ending_type.value,
        "amount_received": _money(result.amount_received),
        "player_briefcase_value": _money(result.player_briefcase_value),
        "accepted_offer": (
            _money(result.accepted_offer) if result.accepted_offer else None
        ),
        "decision_round": result.decision_round,
        "swap_decision": result.swap_decision,
        "final_briefcase_number": result.final_briefcase_number,
        "final_briefcase_value": (
            _money(result.final_briefcase_value)
            if result.final_briefcase_value
            else None
        ),
    }
