"""Unit tests for the GameState offer/decision transitions (Phase 5)."""

import pytest

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.errors import InvalidGameStateError, NoPendingOfferError
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money


def make_in_progress_game() -> GameState:
    game = GameState.create(OFFICIAL_BRIEFCASE_VALUES)
    game.select_player_briefcase(7)
    return game


def open_current_round(game: GameState) -> None:
    to_open = game.openings_required_in_current_round()
    for briefcase in game.available_briefcases()[:to_open]:
        game.open_briefcase(briefcase.number)


def test_offer_requires_a_complete_round() -> None:
    game = make_in_progress_game()
    with pytest.raises(InvalidGameStateError):
        game.set_pending_offer(Money.of("100"))


def test_set_pending_offer_transitions_to_offer_pending() -> None:
    game = make_in_progress_game()
    open_current_round(game)
    game.set_pending_offer(Money.of("100"))
    assert game.status is GameStatus.OFFER_PENDING
    assert game.current_offer == Money.of("100")


def test_accept_offer_ends_the_game() -> None:
    game = make_in_progress_game()
    open_current_round(game)
    game.set_pending_offer(Money.of("100"))
    accepted = game.accept_offer()
    assert accepted == Money.of("100")
    assert game.status is GameStatus.ACCEPTED
    assert game.is_over() is True


def test_cannot_accept_twice() -> None:
    game = make_in_progress_game()
    open_current_round(game)
    game.set_pending_offer(Money.of("100"))
    game.accept_offer()
    with pytest.raises(NoPendingOfferError):
        game.accept_offer()


def test_accept_without_pending_offer_raises() -> None:
    game = make_in_progress_game()
    with pytest.raises(NoPendingOfferError):
        game.accept_offer()


def test_reject_on_non_final_round_returns_to_in_progress() -> None:
    game = make_in_progress_game()
    open_current_round(game)
    game.set_pending_offer(Money.of("100"))
    game.reject_offer()
    assert game.status is GameStatus.IN_PROGRESS
    assert game.current_offer is None
    game.advance_to_next_round()
    assert game.current_round == 2


def test_reject_on_final_round_moves_to_final_swap_pending() -> None:
    game = make_in_progress_game()
    for _ in range(8):  # rounds 1..8
        open_current_round(game)
        game.set_pending_offer(Money.of("1"))
        game.reject_offer()
        game.advance_to_next_round()
    assert game.current_round == 9
    open_current_round(game)
    game.set_pending_offer(Money.of("1"))
    game.reject_offer()
    assert game.status is GameStatus.FINAL_SWAP_PENDING
    assert game.is_over() is False


def test_cannot_open_after_accepting() -> None:
    game = make_in_progress_game()
    open_current_round(game)
    game.set_pending_offer(Money.of("100"))
    game.accept_offer()
    other = game.available_briefcases()[0]
    with pytest.raises(InvalidGameStateError):
        game.open_briefcase(other.number)
