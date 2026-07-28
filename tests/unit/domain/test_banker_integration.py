"""Minimal integration tests between the banker strategy and GameState.

A deterministic distribution (values 1..26 in briefcase order) is used so the
offers can be asserted exactly. No randomness is involved.
"""

from tont_game.domain.entities.game_state import GameState
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.value_objects.money import Money


def make_game() -> GameState:
    values = [Money.of(n) for n in range(1, 27)]  # briefcase i holds value i
    game = GameState.create(values)
    game.select_player_briefcase(10)  # player holds value 10
    return game


def open_current_round(game: GameState) -> None:
    to_open = game.openings_required_in_current_round()
    for briefcase in game.available_briefcases()[:to_open]:
        game.open_briefcase(briefcase.number)


def test_offer_uses_remaining_values_from_game_state() -> None:
    game = make_game()
    strategy = DefaultBankerStrategy()
    # sum(1..26) = 351; mean = 351/26 = 13.5; round 1 (35%) -> 4.725 -> 4.73
    offer = strategy.offer(game.remaining_values(), game.current_round)
    assert offer == Money.of("4.73")


def test_player_value_is_included_in_the_offer_base() -> None:
    game = make_game()
    strategy = DefaultBankerStrategy()
    # The player's value (10) is part of remaining_values.
    assert game.player_briefcase is not None
    assert game.player_briefcase.value in game.remaining_values()
    assert len(game.remaining_values()) == 26
    # The exact offer (4.73) only holds if all 26 values, incl. the player's,
    # are averaged.
    assert strategy.offer(game.remaining_values(), game.current_round) == Money.of(
        "4.73"
    )


def test_remaining_values_semantics_behind_the_offer() -> None:
    game = make_game()  # player holds value 10
    open_current_round(game)  # opens the six lowest available: values 1..6
    remaining = game.remaining_values()

    # Opened values are excluded from the offer base.
    for opened in game.opened_briefcases():
        assert opened.value not in remaining
    # The protected player's value is always included.
    assert game.player_briefcase is not None
    assert game.player_briefcase.value in remaining
    # Eligible still-closed values are included (e.g. briefcase 7, value 7).
    assert game.briefcase(7).value in remaining


def test_offer_is_recomputed_after_opening_briefcases() -> None:
    game = make_game()
    strategy = DefaultBankerStrategy()
    initial = strategy.offer(game.remaining_values(), game.current_round)

    # Round 1 opens the six lowest available briefcases: values 1..6
    # (player is 10). Remaining sum = 351 - 21 = 330 over 20 values; mean 16.5.
    open_current_round(game)
    after_opening = strategy.offer(game.remaining_values(), game.current_round)
    assert initial == Money.of("4.73")
    assert after_opening == Money.of("5.78")  # 16.5 * 0.35 = 5.775 -> 5.78
    assert after_opening > initial  # eliminating the lowest values raised the mean

    # Advancing to round 2 (40%) with the same remaining values: 16.5 * 0.40.
    game.advance_to_next_round()
    round_two = strategy.offer(game.remaining_values(), game.current_round)
    assert round_two == Money.of("6.60")
