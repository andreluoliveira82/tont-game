"""Unit tests for the GameState endgame primitives (Phase 5.5)."""

import pytest

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.errors import InvalidGameStateError
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money


def _open_current_round(game: GameState) -> None:
    to_open = game.openings_required_in_current_round()
    for briefcase in game.available_briefcases()[:to_open]:
        game.open_briefcase(briefcase.number)


def reach_final_swap_pending(player: int = 7) -> GameState:
    game = GameState.create(OFFICIAL_BRIEFCASE_VALUES)
    game.select_player_briefcase(player)
    for _ in range(8):  # rounds 1..8
        _open_current_round(game)
        game.set_pending_offer(Money.of("1"))
        game.reject_offer()
        game.advance_to_next_round()
    _open_current_round(game)  # round 9 opens the single briefcase
    game.set_pending_offer(Money.of("1"))
    game.reject_offer()
    return game


def test_reaches_final_swap_pending_with_two_closed() -> None:
    game = reach_final_swap_pending()
    assert game.status is GameStatus.FINAL_SWAP_PENDING
    assert game.closed_briefcase_count() == 2
    assert len(game.available_briefcases()) == 1


# --- apply_final_swap -------------------------------------------------------


def test_apply_final_swap_changes_player_briefcase() -> None:
    game = reach_final_swap_pending()
    other = game.available_briefcases()[0]
    game.apply_final_swap()
    assert game.player_briefcase is not None
    assert game.player_briefcase.number == other.number
    assert game.status is GameStatus.FINAL_SWAP_PENDING


def test_apply_final_swap_only_in_final_swap_pending() -> None:
    game = GameState.create(OFFICIAL_BRIEFCASE_VALUES)
    game.select_player_briefcase(7)
    with pytest.raises(InvalidGameStateError):
        game.apply_final_swap()


def test_apply_final_swap_cannot_happen_twice() -> None:
    game = reach_final_swap_pending()
    game.apply_final_swap()
    with pytest.raises(InvalidGameStateError):
        game.apply_final_swap()


# --- reveal_final_and_finish ------------------------------------------------


def test_reveal_without_swap_keeps_original_as_final() -> None:
    game = reach_final_swap_pending()
    original = game.player_briefcase
    assert original is not None
    final_value = game.reveal_final_and_finish()
    assert game.status is GameStatus.FINISHED
    assert game.is_over() is True
    assert final_value == original.value
    assert game.player_briefcase is not None
    assert game.player_briefcase.number == original.number


def test_reveal_with_swap_makes_other_briefcase_final() -> None:
    game = reach_final_swap_pending()
    other = game.available_briefcases()[0]
    other_value = other.value
    game.apply_final_swap()
    final_value = game.reveal_final_and_finish()
    assert final_value == other_value
    assert game.player_briefcase is not None
    assert game.player_briefcase.number == other.number
    assert game.status is GameStatus.FINISHED


def test_reveal_opens_the_two_last_briefcases() -> None:
    game = reach_final_swap_pending()
    assert game.closed_briefcase_count() == 2
    game.reveal_final_and_finish()
    assert game.closed_briefcase_count() == 0
    assert len(game.opened_briefcases()) == 26


def test_reveal_only_in_final_swap_pending() -> None:
    game = GameState.create(OFFICIAL_BRIEFCASE_VALUES)
    game.select_player_briefcase(7)
    with pytest.raises(InvalidGameStateError):
        game.reveal_final_and_finish()


def test_cannot_reveal_twice() -> None:
    game = reach_final_swap_pending()
    game.reveal_final_and_finish()
    with pytest.raises(InvalidGameStateError):
        game.reveal_final_and_finish()


# --- no operation after FINISHED --------------------------------------------


def test_no_swap_after_finished() -> None:
    game = reach_final_swap_pending()
    game.reveal_final_and_finish()
    with pytest.raises(InvalidGameStateError):
        game.apply_final_swap()


def test_no_open_after_finished() -> None:
    game = reach_final_swap_pending()
    game.reveal_final_and_finish()
    with pytest.raises(InvalidGameStateError):
        game.open_briefcase(7)
