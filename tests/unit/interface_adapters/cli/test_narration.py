"""Unit tests for the pure ending-narration module (Phase 10.5).

The game's ``max_value``/``min_value`` are fixed at 100 and 1 here so the
``got``/``gave_up`` facts can exercise the classification independently.
"""

from tont_game.domain.value_objects.money import Money
from tont_game.interface_adapters.cli import narration
from tont_game.interface_adapters.cli.narration import EndingMoment

MAX = Money.of("100")
MIN = Money.of("1")


def test_peak_when_got_is_the_max() -> None:
    moment = narration.moment_for(
        got=Money.of("100"), gave_up=Money.of("10"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.PEAK


def test_floor_when_got_is_the_min() -> None:
    moment = narration.moment_for(
        got=Money.of("1"), gave_up=Money.of("50"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.FLOOR


def test_triumph_when_got_is_at_least_double() -> None:
    moment = narration.moment_for(
        got=Money.of("20"), gave_up=Money.of("10"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.TRIUMPH


def test_regret_when_gave_up_is_at_least_double() -> None:
    moment = narration.moment_for(
        got=Money.of("10"), gave_up=Money.of("20"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.REGRET


def test_silence_when_values_are_close() -> None:
    assert (
        narration.moment_for(
            got=Money.of("12"), gave_up=Money.of("10"), max_value=MAX, min_value=MIN
        )
        is None
    )
    assert (
        narration.moment_for(
            got=Money.of("10"), gave_up=Money.of("12"), max_value=MAX, min_value=MIN
        )
        is None
    )


def test_just_below_double_is_silence_both_ways() -> None:
    assert (
        narration.moment_for(
            got=Money.of("19"), gave_up=Money.of("10"), max_value=MAX, min_value=MIN
        )
        is None
    )
    assert (
        narration.moment_for(
            got=Money.of("10"), gave_up=Money.of("19"), max_value=MAX, min_value=MIN
        )
        is None
    )


def test_peak_takes_precedence_over_triumph() -> None:
    # got is the max and also at least double the alternative: PEAK must win.
    moment = narration.moment_for(
        got=Money.of("100"), gave_up=Money.of("10"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.PEAK


def test_floor_takes_precedence_over_regret() -> None:
    # got is the min and the alternative is at least double: FLOOR must win.
    moment = narration.moment_for(
        got=Money.of("1"), gave_up=Money.of("50"), max_value=MAX, min_value=MIN
    )
    assert moment is EndingMoment.FLOOR


def test_every_moment_has_a_non_empty_message_bank() -> None:
    for moment in EndingMoment:
        variants = narration.messages(moment)
        assert isinstance(variants, tuple)
        assert len(variants) >= 1
        assert all(isinstance(text, str) and text for text in variants)
