"""Integration tests for the normal game flow up to a Topa (no CLI, no endgame).

Uses the shared ``driver`` / ``moment`` fixtures (see conftest), which wrap the
real Application use cases.
"""

from tont_game.domain.history.records import Decision, EndingType
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money


def test_topa_on_first_round_full_flow(driver, moment) -> None:
    driver.select(10)  # player holds value 10
    driver.open_full_round()  # opens values 1..6
    offer = driver.make_offer()
    driver.decide(Decision.ACCEPT)

    record = driver.record
    result = record.official_result
    assert result is not None
    assert result.ending_type is EndingType.OFFER_ACCEPTED
    assert result.amount_received == offer == Money.of("5.78")
    assert result.player_briefcase_value == Money.of(10)
    assert result.decision_round == 1
    assert record.finished_at == moment
    assert driver.state.is_over() is True

    assert len(record.rounds) == 1
    assert len(record.rounds[0].openings) == 6
    assert record.rounds[0].decision is Decision.ACCEPT
    assert record.seed == 7
    assert len(record.initial_distribution) == 26


def test_reject_then_accept_across_rounds(driver) -> None:
    driver.select(10)

    driver.open_full_round()
    driver.make_offer()
    driver.decide(Decision.REJECT)
    assert driver.state.current_round == 2

    driver.open_full_round()
    driver.make_offer()
    driver.decide(Decision.ACCEPT)

    record = driver.record
    assert record.official_result is not None
    assert record.official_result.decision_round == 2
    assert len(record.rounds) == 2
    assert record.rounds[0].decision is Decision.REJECT
    assert record.rounds[1].decision is Decision.ACCEPT


def test_reject_all_reaches_final_swap_pending_without_official_result(driver) -> None:
    driver.reject_until_endgame(10)

    record = driver.record
    assert driver.state.status is GameStatus.FINAL_SWAP_PENDING
    assert driver.state.is_over() is False
    # Endgame is resolved by DecideFinalSwap: no official result until then.
    assert record.official_result is None
    assert len(record.rounds) == 9
    assert all(r.decision is Decision.REJECT for r in record.rounds)
