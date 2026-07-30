"""Unit tests for the public game-record JSON schema (Phase 11)."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.history.records import Decision, EndingType, OfficialResult
from tont_game.domain.value_objects.money import Money
from tont_game.infrastructure.persistence.game_record_schema import (
    SCHEMA_VERSION,
    detail_from_dict,
    serialize,
    summary_from_dict,
)


def topa_record() -> GameRecord:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("250"))],
        seed=7,
    )
    record.record_player_briefcase(2)
    record.record_opening(1, 1, Money.of("100"))
    record.record_offer(1, Money.of("120.50"), Decimal("0.35"), (Money.of("250"),))
    record.record_decision(1, Decision.ACCEPT)
    record.close(
        OfficialResult.from_accepted_offer(
            decision_round=1,
            accepted_offer=Money.of("120.50"),
            player_briefcase_value=Money.of("250"),
        ),
        datetime(2026, 7, 29, 1, tzinfo=UTC),
    )
    return record


def endgame_swap_record() -> GameRecord:
    record = GameRecord(
        game_id=uuid4(),
        started_at=datetime(2026, 7, 29, tzinfo=UTC),
        initial_distribution=[(1, Money.of("100")), (2, Money.of("250"))],
    )
    record.record_player_briefcase(1)
    record.close(
        OfficialResult.from_final_reveal(
            swap_decision=True,
            player_briefcase_value=Money.of("100"),
            final_briefcase_number=2,
            final_briefcase_value=Money.of("250"),
        ),
        datetime(2026, 7, 29, 2, tzinfo=UTC),
    )
    return record


def test_serialize_exposes_a_versioned_explicit_schema() -> None:
    data = serialize(topa_record())
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["seed"] == 7
    assert data["player_briefcase"] == 2
    # Money is stored as a decimal string, never as a float.
    assert data["initial_distribution"][0] == {"briefcase": 1, "value": "100.00"}
    assert data["official_result"]["amount_received"] == "120.50"
    assert data["official_result"]["ending_type"] == "OFFER_ACCEPTED"
    assert data["rounds"][0]["offer"]["percentage"] == "0.35"
    assert data["rounds"][0]["decision"] == "ACCEPT"


def test_summary_round_trip_for_topa() -> None:
    record = topa_record()
    summary = summary_from_dict(serialize(record))
    assert summary.game_id == record.game_id
    assert summary.ending_type is EndingType.OFFER_ACCEPTED
    assert summary.amount_received == Money.of("120.50")
    assert summary.player_briefcase_value == Money.of("250")


def test_serialize_endgame_swap_result() -> None:
    data = serialize(endgame_swap_record())
    result = data["official_result"]
    assert result["ending_type"] == "FINAL_REVEAL_WITH_SWAP"
    assert result["swap_decision"] is True
    assert result["final_briefcase_number"] == 2
    assert result["final_briefcase_value"] == "250.00"
    assert result["accepted_offer"] is None


def test_detail_round_trip_reconstructs_the_full_game() -> None:
    record = topa_record()
    detail = detail_from_dict(serialize(record))
    assert detail.game_id == record.game_id
    assert detail.seed == 7
    assert detail.player_briefcase == 2
    assert detail.ending_type is EndingType.OFFER_ACCEPTED
    assert detail.amount_received == Money.of("120.50")
    assert len(detail.rounds) == 1
    round_one = detail.rounds[0]
    assert round_one.round_number == 1
    assert round_one.openings == ((1, Money.of("100")),)
    assert round_one.offer == Money.of("120.50")
    assert round_one.decision is Decision.ACCEPT


def test_unknown_future_schema_version_is_rejected() -> None:
    data = serialize(topa_record())
    data["schema_version"] = SCHEMA_VERSION + 1
    with pytest.raises(ValueError, match="schema version"):
        detail_from_dict(data)
    with pytest.raises(ValueError, match="schema version"):
        summary_from_dict(data)
