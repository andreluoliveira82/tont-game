"""Unit tests for the Money value object."""

from decimal import Decimal

import pytest

from tont_game.domain.value_objects.money import Money


def test_money_is_quantized_to_cents() -> None:
    assert Money.of("1").amount == Decimal("1.00")
    assert Money.of(Decimal("1.005")).amount == Decimal("1.01")  # HALF_UP


def test_money_equality_ignores_trailing_precision() -> None:
    assert Money.of("0.5") == Money.of(Decimal("0.50"))
    assert hash(Money.of("0.5")) == hash(Money.of("0.50"))


def test_money_ordering() -> None:
    assert Money.of("1.00") < Money.of("2.00")
    assert sorted([Money.of("5"), Money.of("1"), Money.of("3")]) == [
        Money.of("1"),
        Money.of("3"),
        Money.of("5"),
    ]


def test_money_rejects_float() -> None:
    with pytest.raises(TypeError):
        Money.of(1.5)  # type: ignore[arg-type]


def test_money_rejects_bool() -> None:
    with pytest.raises(TypeError):
        Money.of(True)  # type: ignore[arg-type]


def test_money_rejects_negative() -> None:
    with pytest.raises(ValueError):
        Money.of("-0.01")


def test_money_accepts_int_and_str_and_decimal() -> None:
    assert Money.of(1000) == Money.of("1000") == Money.of(Decimal("1000"))


def test_money_is_immutable() -> None:
    money = Money.of("10")
    with pytest.raises(AttributeError):
        money.amount = Decimal("20")  # type: ignore[misc]
