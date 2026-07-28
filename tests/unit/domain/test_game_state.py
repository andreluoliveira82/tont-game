"""Unit tests for the GameState aggregate."""

import pytest

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.errors import (
    BriefcaseAlreadyOpenedError,
    GameConfigurationError,
    InvalidBriefcaseNumberError,
    InvalidGameStateError,
    NoMoreRoundsError,
    PlayerBriefcaseProtectedError,
    RoundLimitExceededError,
    RoundNotCompleteError,
)
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money
from tont_game.domain.value_objects.round_schedule import (
    DEFAULT_ROUND_OPENINGS,
    RoundSchedule,
)


def make_game() -> GameState:
    return GameState.create(OFFICIAL_BRIEFCASE_VALUES)


def open_current_round(game: GameState) -> None:
    """Open exactly the required briefcases for the current round."""
    to_open = game.openings_required_in_current_round()
    for briefcase in game.available_briefcases()[:to_open]:
        game.open_briefcase(briefcase.number)


# --- creation ---------------------------------------------------------------


def test_new_game_has_twenty_six_closed_briefcases() -> None:
    game = make_game()
    assert len(game.all_briefcases()) == 26
    assert game.closed_briefcase_count() == 26
    assert len(game.remaining_values()) == 26


def test_new_game_starts_not_started_without_player() -> None:
    game = make_game()
    assert game.status is GameStatus.NOT_STARTED
    assert game.player_briefcase is None


def test_create_rejects_wrong_number_of_values() -> None:
    with pytest.raises(GameConfigurationError):
        GameState.create(OFFICIAL_BRIEFCASE_VALUES[:25])


def test_create_rejects_schedule_that_does_not_leave_two_closed() -> None:
    bad_schedule = RoundSchedule(openings=(6, 5, 4, 3, 2, 1))  # opens 21, not 24
    with pytest.raises(GameConfigurationError):
        GameState.create(OFFICIAL_BRIEFCASE_VALUES, schedule=bad_schedule)


# --- player selection -------------------------------------------------------


def test_selecting_player_starts_game_and_protects_briefcase() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    assert game.status is GameStatus.IN_PROGRESS
    assert game.player_briefcase is not None
    assert game.player_briefcase.number == 7
    assert all(case.number != 7 for case in game.available_briefcases())
    assert len(game.available_briefcases()) == 25


def test_player_value_stays_in_remaining_values() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    player_value = game.player_briefcase.value
    assert player_value in game.remaining_values()
    open_current_round(game)
    assert player_value in game.remaining_values()


def test_selecting_invalid_briefcase_raises() -> None:
    game = make_game()
    with pytest.raises(InvalidBriefcaseNumberError):
        game.select_player_briefcase(99)


def test_selecting_player_twice_raises() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    with pytest.raises(InvalidGameStateError):
        game.select_player_briefcase(8)


# --- opening briefcases -----------------------------------------------------


def test_cannot_open_before_selecting_player() -> None:
    game = make_game()
    with pytest.raises(InvalidGameStateError):
        game.open_briefcase(1)


def test_opening_reveals_value_and_removes_it_from_remaining() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    target = game.available_briefcases()[0]
    game.open_briefcase(target.number)
    assert target.opened is True
    assert game.closed_briefcase_count() == 25
    assert list(game.remaining_values()).count(target.value) == (
        OFFICIAL_BRIEFCASE_VALUES.count(target.value) - 1
    )


def test_cannot_open_player_briefcase() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    with pytest.raises(PlayerBriefcaseProtectedError):
        game.open_briefcase(7)


def test_cannot_open_already_opened_briefcase() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    target = game.available_briefcases()[0]
    game.open_briefcase(target.number)
    with pytest.raises(BriefcaseAlreadyOpenedError):
        game.open_briefcase(target.number)


def test_cannot_open_more_than_round_allows() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    open_current_round(game)  # opens the 6 allowed in round 1
    extra = game.available_briefcases()[0]
    with pytest.raises(RoundLimitExceededError):
        game.open_briefcase(extra.number)


# --- round progression ------------------------------------------------------


def test_cannot_advance_before_round_is_complete() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    with pytest.raises(RoundNotCompleteError):
        game.advance_to_next_round()


def test_advancing_moves_to_next_round_and_resets_openings() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    open_current_round(game)
    game.advance_to_next_round()
    assert game.current_round == 2
    assert game.openings_required_in_current_round() == 5
    assert game.openings_remaining_in_current_round() == 5


def test_full_playthrough_leaves_exactly_two_closed_briefcases() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    for _ in range(len(DEFAULT_ROUND_OPENINGS)):
        open_current_round(game)
        if game.has_next_round():
            game.advance_to_next_round()

    assert game.all_rounds_completed() is True
    assert game.has_next_round() is False
    assert len(game.opened_briefcases()) == 24
    assert game.closed_briefcase_count() == 2
    # Exactly the player briefcase and one available briefcase remain closed.
    assert game.player_briefcase in game.closed_briefcases()
    assert len(game.available_briefcases()) == 1


def test_cannot_advance_past_last_round() -> None:
    game = make_game()
    game.select_player_briefcase(7)
    for _ in range(len(DEFAULT_ROUND_OPENINGS)):
        open_current_round(game)
        if game.has_next_round():
            game.advance_to_next_round()
    with pytest.raises(NoMoreRoundsError):
        game.advance_to_next_round()


def test_remaining_values_include_player_value_of_known_distribution() -> None:
    # Deterministic distribution: values 1..26 in briefcase order.
    values = [Money.of(n) for n in range(1, 27)]
    game = GameState.create(values)
    game.select_player_briefcase(10)
    assert game.player_briefcase.value == Money.of(10)
    assert Money.of(10) in game.remaining_values()
