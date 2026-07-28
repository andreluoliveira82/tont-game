"""Unit tests for the official briefcase values."""

from decimal import Decimal

from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.value_objects.money import Money


def test_there_are_exactly_twenty_six_values() -> None:
    assert len(OFFICIAL_BRIEFCASE_VALUES) == 26


def test_all_values_are_money() -> None:
    assert all(isinstance(value, Money) for value in OFFICIAL_BRIEFCASE_VALUES)


def test_each_value_appears_exactly_once() -> None:
    assert len(set(OFFICIAL_BRIEFCASE_VALUES)) == 26


def test_smallest_and_largest_values() -> None:
    assert min(OFFICIAL_BRIEFCASE_VALUES) == Money.of(Decimal("0.50"))
    assert max(OFFICIAL_BRIEFCASE_VALUES) == Money.of(Decimal("2000000.00"))
