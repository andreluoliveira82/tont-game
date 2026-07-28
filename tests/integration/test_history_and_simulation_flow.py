"""Integration tests: full history verification, post-game simulation, and
offer oscillation across rounds. Uses the shared conftest fixtures.
"""

from tont_game.domain.history.records import Decision
from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.domain.simulation.post_game_simulation import SimulationScenario
from tont_game.domain.value_objects.money import Money


def test_topa_full_history_is_coherent(driver) -> None:
    driver.select(10)  # player holds value 10
    driver.open_full_round()  # opens 1..6
    offer = driver.make_offer()
    driver.decide(Decision.ACCEPT)

    record = driver.record
    # Initial distribution: the concrete historical fact (26 pairs).
    assert record.initial_distribution == tuple((n, Money.of(n)) for n in range(1, 27))
    assert record.player_briefcase_number == 10

    round_one = record.rounds[0]
    assert [o.briefcase_number for o in round_one.openings] == [1, 2, 3, 4, 5, 6]
    assert [o.value for o in round_one.openings] == [Money.of(n) for n in range(1, 7)]
    assert round_one.offer is not None
    assert round_one.offer.offer == offer
    assert round_one.offer.percentage == DefaultBankerStrategy().percentage_for_round(1)
    assert round_one.decision is Decision.ACCEPT

    result = record.official_result
    assert result is not None
    assert result.amount_received == offer
    assert result.player_briefcase_value == Money.of(10)
    # Coherence: final state, history and official result agree.
    assert driver.state.is_over() is True
    assert record.finished_at is not None


def test_topa_then_simulation_does_not_change_history(driver) -> None:
    driver.select(10)
    driver.open_full_round()
    offer = driver.make_offer()
    driver.decide(Decision.ACCEPT)

    record = driver.record
    official_before = record.official_result
    rounds_before = record.rounds

    simulation = driver.simulate()

    assert simulation.scenario is SimulationScenario.CONTINUE_HOLD
    assert simulation.hypothetical_amount == Money.of(10)  # player briefcase value
    assert simulation.official_amount == offer
    # The simulation is a pure derivation: nothing in the record changed.
    assert record.official_result is official_before
    assert record.rounds == rounds_before


def test_offers_vary_across_rounds(driver) -> None:
    driver.select(10)
    offers = []
    for _ in range(5):  # rounds 1..5, rejecting each
        driver.open_full_round()
        offers.append(driver.make_offer())
        driver.decide(Decision.REJECT)
    # Multiple offers were made and the offer is not constant across rounds.
    assert len(offers) == 5
    assert len(set(offers)) > 1


def test_offer_is_lower_when_high_values_are_eliminated(make_driver) -> None:
    # Same game/distribution; only the choice of which briefcases to open differs.
    low = make_driver()
    low.select(10)
    for briefcase in low.state.available_briefcases()[:6]:  # open the 6 lowest
        low.open_briefcase(briefcase.number)
    offer_low = low.make_offer()

    high = make_driver()
    high.select(10)
    for briefcase in high.state.available_briefcases()[-6:]:  # open the 6 highest
        high.open_briefcase(briefcase.number)
    offer_high = high.make_offer()

    # Eliminating high values lowers the mean of the remaining values, so the
    # offer is lower — no monotonicity is enforced.
    assert offer_high < offer_low
