"""Unit tests for the value distribution service.

These tests use a deterministic test double (no ``random`` import) to prove
the service is independent of any concrete randomness implementation.
"""

from collections.abc import Sequence
from typing import TypeVar

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.randomness import RandomSource
from tont_game.domain.services.distribution import create_shuffled_game
from tont_game.domain.value_objects.money import Money

T = TypeVar("T")


class ReversingRandomSource:
    """Deterministic double: 'shuffles' by reversing the sequence."""

    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(reversed(list(items)))


def test_double_satisfies_random_source_protocol() -> None:
    assert isinstance(ReversingRandomSource(), RandomSource)


def test_distribution_keeps_all_official_values_exactly_once() -> None:
    game = create_shuffled_game(ReversingRandomSource())
    values = [briefcase.value for briefcase in game.all_briefcases()]
    assert len(values) == 26
    assert sorted(values) == sorted(OFFICIAL_BRIEFCASE_VALUES)
    assert len(set(values)) == 26


def test_each_briefcase_receives_exactly_one_money_value() -> None:
    game = create_shuffled_game(ReversingRandomSource())
    briefcases = game.all_briefcases()
    assert len(briefcases) == 26
    assert all(isinstance(briefcase.value, Money) for briefcase in briefcases)


def test_service_uses_the_injected_source_order() -> None:
    game = create_shuffled_game(ReversingRandomSource())
    actual = [briefcase.value for briefcase in game.all_briefcases()]
    assert actual == list(reversed(OFFICIAL_BRIEFCASE_VALUES))


def test_returns_a_valid_initial_game_state() -> None:
    game = create_shuffled_game(ReversingRandomSource())
    assert isinstance(game, GameState)
    assert game.closed_briefcase_count() == 26


def test_accepts_custom_values() -> None:
    values = [Money.of(n) for n in range(1, 27)]
    game = create_shuffled_game(ReversingRandomSource(), values=values)
    actual = [briefcase.value for briefcase in game.all_briefcases()]
    assert actual == list(reversed(values))
