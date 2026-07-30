"""Unit tests for the composition-root argument handling."""

from tont_game.__main__ import _parse_seed, _select_command


def test_no_args_means_random_game() -> None:
    assert _parse_seed([]) is None


def test_integer_argument_is_used_as_seed() -> None:
    assert _parse_seed(["42"]) == 42


def test_non_integer_argument_is_ignored() -> None:
    assert _parse_seed(["abc"]) is None


def test_history_argument_selects_the_history_command() -> None:
    assert _select_command(["history"]) == "history"


def test_no_args_selects_the_play_command() -> None:
    assert _select_command([]) == "play"


def test_seed_argument_selects_the_play_command() -> None:
    assert _select_command(["42"]) == "play"
