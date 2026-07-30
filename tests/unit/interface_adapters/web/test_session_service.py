"""Headless tests for the web SessionService (Sprint 1).

Uses the identity shuffle (see conftest), so briefcase ``i`` holds the ``i``-th
official value. The player keeps briefcase 10 (R$ 500,00); the last closed
briefcase is 26 (R$ 2.000.000,00).
"""

import pytest

from tont_game.interface_adapters.web.session_service import (
    SessionService,
    UnknownSessionError,
)

QUOTAS = [6, 5, 4, 3, 2, 1, 1, 1, 1]


def openable(player: int) -> list[int]:
    return [n for n in range(1, 27) if n != player]


def open_quota(service: SessionService, sid: str, numbers: list[int]) -> dict:
    view: dict = {}
    for number in numbers:
        view = service.act(sid, "open_briefcase", {"number": number})
    return view


def test_start_asks_to_select_a_briefcase(web_service: SessionService) -> None:
    _, view = web_service.start()
    assert view["status"] == "NOT_STARTED"
    assert view["available_actions"] == ["select_briefcase"]
    assert view["player_briefcase"] is None


def test_full_topa_flow_then_simulation(web_service: SessionService) -> None:
    sid, _ = web_service.start()

    view = web_service.act(sid, "select_briefcase", {"number": 10})
    assert view["status"] == "IN_PROGRESS"
    assert view["available_actions"] == ["open_briefcase"]
    assert view["openings_remaining"] == 6
    assert 10 not in view["available_briefcases"]
    assert view["player_briefcase"] == {"number": 10, "value": None}

    view = open_quota(web_service, sid, [1, 2, 3, 4, 5, 6])
    assert view["status"] == "OFFER_PENDING"
    assert view["current_offer"] is not None
    assert view["available_actions"] == ["decide"]

    view = web_service.act(sid, "decide", {"accept": True})
    assert view["status"] == "ACCEPTED"
    assert view["official_result"]["ending_type"] == "OFFER_ACCEPTED"
    assert view["player_briefcase"]["value"] == "500.00"  # revealed at the end
    assert view["available_actions"] == ["simulate"]

    view = web_service.act(sid, "simulate")
    assert view["simulation"]["hypothetical"] == "500.00"
    assert view["available_actions"] == []


def test_reject_everything_reaches_endgame_and_reveals(
    web_service: SessionService,
) -> None:
    sid, _ = web_service.start()
    web_service.act(sid, "select_briefcase", {"number": 10})

    numbers = openable(10)
    index = 0
    view: dict = {}
    for quota in QUOTAS:
        open_quota(web_service, sid, numbers[index : index + quota])
        index += quota
        view = web_service.act(sid, "decide", {"accept": False})

    assert view["status"] == "FINAL_SWAP_PENDING"
    assert view["available_actions"] == ["decide_swap"]

    view = web_service.act(sid, "decide_swap", {"swap": False})
    assert view["status"] == "FINISHED"
    assert view["official_result"]["ending_type"] == "FINAL_REVEAL_WITHOUT_SWAP"
    assert view["official_result"]["amount_received"] == "500.00"


def test_invalid_open_returns_an_error_without_advancing(
    web_service: SessionService,
) -> None:
    sid, _ = web_service.start()
    web_service.act(sid, "select_briefcase", {"number": 10})

    view = web_service.act(sid, "open_briefcase", {"number": 10})  # own briefcase
    assert "error" in view
    assert view["status"] == "IN_PROGRESS"
    assert view["openings_remaining"] == 6  # nothing consumed


def test_unknown_session_raises(web_service: SessionService) -> None:
    with pytest.raises(UnknownSessionError):
        web_service.act("nope", "select_briefcase", {"number": 1})
