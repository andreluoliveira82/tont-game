"""Unit tests for the banker strategy in isolation."""

from collections.abc import Sequence
from decimal import Decimal

import pytest

from tont_game.domain.errors import BankerStrategyError
from tont_game.domain.services.banker import (
    DEFAULT_BANKER_PERCENTAGES,
    BankerStrategy,
    DefaultBankerStrategy,
)
from tont_game.domain.value_objects.money import Money
from tont_game.domain.value_objects.round_schedule import RoundSchedule


def money_list(*amounts: str) -> list[Money]:
    return [Money.of(amount) for amount in amounts]


def test_default_percentages_match_the_official_nine_rounds() -> None:
    # The official default configuration must stay consistent with the game:
    # exactly nine percentages, one per official round. Checked at test level
    # so BankerStrategy is not structurally coupled to RoundSchedule.
    assert len(DEFAULT_BANKER_PERCENTAGES) == RoundSchedule().total_rounds == 9
    expected = (
        Decimal("0.35"),
        Decimal("0.40"),
        Decimal("0.50"),
        Decimal("0.60"),
        Decimal("0.70"),
        Decimal("0.80"),
        Decimal("0.85"),
        Decimal("0.90"),
        Decimal("0.95"),
    )
    assert expected == DEFAULT_BANKER_PERCENTAGES


# --- protocol / substitutability -------------------------------------------


def test_default_strategy_satisfies_protocol() -> None:
    assert isinstance(DefaultBankerStrategy(), BankerStrategy)


def test_a_custom_strategy_is_substitutable() -> None:
    class FixedOfferStrategy:
        def offer(self, remaining_values: Sequence[Money], round_number: int) -> Money:
            return Money.of("1.00")

    strategy = FixedOfferStrategy()
    assert isinstance(strategy, BankerStrategy)
    assert strategy.offer(money_list("10", "20"), 1) == Money.of("1.00")


# --- formula ----------------------------------------------------------------


def test_offer_is_mean_times_round_percentage() -> None:
    strategy = DefaultBankerStrategy()
    # mean([100, 200, 300, 400]) = 250; round 1 = 35% -> 87.50
    assert strategy.offer(money_list("100", "200", "300", "400"), 1) == Money.of(
        "87.50"
    )


def test_percentage_changes_with_the_round() -> None:
    strategy = DefaultBankerStrategy()
    values = money_list("100", "200", "300", "400")  # mean 250
    assert strategy.offer(values, 3) == Money.of("125.00")  # 50%
    assert strategy.offer(values, 9) == Money.of("237.50")  # 95%


def test_every_round_uses_its_documented_percentage() -> None:
    strategy = DefaultBankerStrategy()
    values = money_list("100")  # mean 100 -> offer equals percentage * 100
    for round_number, percentage in enumerate(DEFAULT_BANKER_PERCENTAGES, start=1):
        expected = Money.of(Decimal("100") * percentage)
        assert strategy.offer(values, round_number) == expected


def test_final_result_is_rounded_half_up_to_cents() -> None:
    strategy = DefaultBankerStrategy()
    # mean([1.00, 1.01, 1.02]) = 1.01; round 3 = 50% -> 0.5050 -> 0.51
    assert strategy.offer(money_list("1.00", "1.01", "1.02"), 3) == Money.of("0.51")


def test_offer_keeps_decimal_precision() -> None:
    strategy = DefaultBankerStrategy()
    offer = strategy.offer(money_list("0.50", "0.01"), 1)
    assert isinstance(offer.amount, Decimal)


# --- invalid inputs ---------------------------------------------------------


def test_unknown_round_is_rejected() -> None:
    strategy = DefaultBankerStrategy()
    with pytest.raises(BankerStrategyError):
        strategy.offer(money_list("100"), 0)
    with pytest.raises(BankerStrategyError):
        strategy.offer(money_list("100"), 10)


def test_empty_remaining_values_is_rejected() -> None:
    strategy = DefaultBankerStrategy()
    with pytest.raises(BankerStrategyError):
        strategy.offer([], 1)


def test_invalid_percentage_configuration_is_rejected() -> None:
    with pytest.raises(BankerStrategyError):
        DefaultBankerStrategy(percentages=())
    with pytest.raises(BankerStrategyError):
        DefaultBankerStrategy(percentages=(Decimal("-0.10"),))
    with pytest.raises(BankerStrategyError):
        DefaultBankerStrategy(percentages=(Decimal("1.50"),))
    with pytest.raises(BankerStrategyError):
        DefaultBankerStrategy(percentages=(0.35,))  # type: ignore[arg-type]


def test_custom_percentages_are_used() -> None:
    strategy = DefaultBankerStrategy(percentages=(Decimal("1.00"),))
    # mean([100, 200]) = 150; 100% -> 150.00
    assert strategy.offer(money_list("100", "200"), 1) == Money.of("150.00")
    with pytest.raises(BankerStrategyError):
        strategy.offer(money_list("100", "200"), 2)  # only round 1 configured


# --- oscillation / no artificial monotonicity -------------------------------


def test_offer_rises_when_low_values_are_eliminated() -> None:
    strategy = DefaultBankerStrategy()
    before = strategy.offer(money_list("100", "900"), 1)  # mean 500 * 0.35 = 175.00
    after = strategy.offer(money_list("900"), 2)  # low removed; 900 * 0.40 = 360.00
    assert before == Money.of("175.00")
    assert after == Money.of("360.00")
    assert after > before


def test_offer_falls_when_high_values_are_eliminated() -> None:
    strategy = DefaultBankerStrategy()
    before = strategy.offer(money_list("100", "900"), 1)  # mean 500 * 0.35 = 175.00
    after = strategy.offer(money_list("100"), 2)  # high removed; 100 * 0.40 = 40.00
    assert before == Money.of("175.00")
    assert after == Money.of("40.00")
    assert after < before


def test_higher_round_percentage_does_not_guarantee_a_higher_offer() -> None:
    strategy = DefaultBankerStrategy()
    # Round 2 (40%) yields a smaller offer than round 1 (35%) because the mean
    # of the remaining values dropped enough to more than offset the higher
    # percentage. No monotonicity is enforced.
    round1 = strategy.offer(money_list("100", "900"), 1)  # 175.00
    round2 = strategy.offer(money_list("100"), 2)  # 40.00
    assert round2 < round1
