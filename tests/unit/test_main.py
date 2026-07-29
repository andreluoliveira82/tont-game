"""Unit tests for the composition-root seed parsing."""

from tont_game.__main__ import _parse_seed


def test_no_args_means_random_game() -> None:
    assert _parse_seed([]) is None


def test_integer_argument_is_used_as_seed() -> None:
    assert _parse_seed(["42"]) == 42


def test_non_integer_argument_is_ignored() -> None:
    assert _parse_seed(["abc"]) is None
