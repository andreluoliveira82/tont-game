"""Integration tests for invalid operations exercised through the use cases.

These raise the domain's invariants at the integrated (use-case) level. Uses
the shared conftest fixtures.
"""

import pytest

from tont_game.domain.errors import (
    BriefcaseAlreadyOpenedError,
    InvalidGameStateError,
    NoPendingOfferError,
    PlayerBriefcaseProtectedError,
    RoundLimitExceededError,
)
from tont_game.domain.history.records import Decision


def test_cannot_open_an_already_opened_briefcase(driver) -> None:
    driver.select(10)
    first = driver.state.available_briefcases()[0]
    driver.open_briefcase(first.number)
    with pytest.raises(BriefcaseAlreadyOpenedError):
        driver.open_briefcase(first.number)


def test_cannot_open_the_player_briefcase(driver) -> None:
    driver.select(10)
    with pytest.raises(PlayerBriefcaseProtectedError):
        driver.open_briefcase(10)


def test_cannot_exceed_the_round_open_limit(driver) -> None:
    driver.select(10)
    driver.open_full_round()  # opens the 6 allowed in round 1
    extra = driver.state.available_briefcases()[0]
    with pytest.raises(RoundLimitExceededError):
        driver.open_briefcase(extra.number)


def test_cannot_decide_without_a_pending_offer(driver) -> None:
    driver.select(10)
    driver.open_full_round()  # round complete, but no offer processed
    with pytest.raises(NoPendingOfferError):
        driver.decide(Decision.ACCEPT)
    assert driver.record.official_result is None


def test_cannot_open_after_topa(driver) -> None:
    driver.select(10)
    driver.open_full_round()
    driver.make_offer()
    driver.decide(Decision.ACCEPT)  # game ends (ACCEPTED)
    other = driver.state.available_briefcases()[0]
    with pytest.raises(InvalidGameStateError):
        driver.open_briefcase(other.number)


def test_cannot_decide_again_after_topa(driver) -> None:
    driver.select(10)
    driver.open_full_round()
    driver.make_offer()
    driver.decide(Decision.ACCEPT)
    with pytest.raises(NoPendingOfferError):
        driver.decide(Decision.REJECT)
