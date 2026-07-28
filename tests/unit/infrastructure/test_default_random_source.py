"""Unit tests for the DefaultRandomSource infrastructure adapter."""

from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.randomness import RandomSource
from tont_game.domain.services.distribution import create_shuffled_game
from tont_game.infrastructure.randomness.random_source import DefaultRandomSource


def test_satisfies_random_source_protocol() -> None:
    assert isinstance(DefaultRandomSource(), RandomSource)


def test_shuffle_preserves_the_multiset() -> None:
    source = DefaultRandomSource(seed=123)
    items = list(range(10))
    shuffled = source.shuffle(items)
    assert sorted(shuffled) == list(range(10))


def test_shuffle_returns_a_new_list_without_mutating_input() -> None:
    source = DefaultRandomSource(seed=1)
    items = [1, 2, 3, 4, 5]
    original = list(items)
    shuffled = source.shuffle(items)
    assert shuffled is not items
    assert items == original


def test_same_seed_reproduces_the_same_distribution() -> None:
    order_a = [
        b.value
        for b in create_shuffled_game(DefaultRandomSource(seed=42)).all_briefcases()
    ]
    order_b = [
        b.value
        for b in create_shuffled_game(DefaultRandomSource(seed=42)).all_briefcases()
    ]
    assert order_a == order_b


def test_different_seeds_produce_different_distributions() -> None:
    order_a = [
        b.value
        for b in create_shuffled_game(DefaultRandomSource(seed=1)).all_briefcases()
    ]
    order_b = [
        b.value
        for b in create_shuffled_game(DefaultRandomSource(seed=2)).all_briefcases()
    ]
    assert order_a != order_b


def test_without_seed_produces_a_valid_distribution() -> None:
    game = create_shuffled_game(DefaultRandomSource())
    values = [b.value for b in game.all_briefcases()]
    assert sorted(values) == sorted(OFFICIAL_BRIEFCASE_VALUES)
    assert len(set(values)) == 26


def test_seed_is_exposed_for_reproducibility() -> None:
    assert DefaultRandomSource(seed=7).seed == 7
    assert DefaultRandomSource().seed is None
