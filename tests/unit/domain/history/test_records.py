"""Unit tests for the immutable history records."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from tont_game.domain.history.records import (
    BankerOfferRecord,
    BriefcaseOpeningRecord,
    Decision,
    EndingType,
    OfficialResult,
)
from tont_game.domain.value_objects.money import Money


def test_opening_record_is_frozen() -> None:
    record = BriefcaseOpeningRecord(briefcase_number=1, value=Money.of("100"))
    with pytest.raises(FrozenInstanceError):
        record.value = Money.of("1")  # type: ignore[misc]


def test_offer_record_holds_audit_facts() -> None:
    record = BankerOfferRecord(
        round_number=1,
        offer=Money.of("50"),
        percentage=Decimal("0.35"),
        remaining_values=(Money.of("100"), Money.of("0")),
    )
    assert record.round_number == 1
    assert record.percentage == Decimal("0.35")
    assert record.remaining_values == (Money.of("100"), Money.of("0"))


def test_decision_has_accept_and_reject() -> None:
    assert {d.name for d in Decision} == {"ACCEPT", "REJECT"}


def test_official_result_from_accepted_offer() -> None:
    result = OfficialResult.from_accepted_offer(
        decision_round=3,
        accepted_offer=Money.of("100"),
        player_briefcase_value=Money.of("250"),
    )
    assert result.ending_type is EndingType.OFFER_ACCEPTED
    assert result.amount_received == Money.of("100")
    assert result.accepted_offer == Money.of("100")
    assert result.player_briefcase_value == Money.of("250")
    assert result.decision_round == 3
    assert result.swap_decision is None


def test_official_result_is_frozen() -> None:
    result = OfficialResult.from_accepted_offer(
        decision_round=1,
        accepted_offer=Money.of("100"),
        player_briefcase_value=Money.of("250"),
    )
    with pytest.raises(FrozenInstanceError):
        result.amount_received = Money.of("1")  # type: ignore[misc]
