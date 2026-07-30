"""Tests for the pure web request routing (Sprint 1)."""

from tont_game.interface_adapters.web.app import handle_api
from tont_game.interface_adapters.web.session_service import SessionService


def test_start_returns_a_session_and_initial_view(web_service: SessionService) -> None:
    status, body = handle_api(web_service, "/api/start", {})
    assert status == 200
    assert body["session_id"]
    assert body["view"]["status"] == "NOT_STARTED"


def test_act_advances_the_game(web_service: SessionService) -> None:
    _, start = handle_api(web_service, "/api/start", {})
    sid = start["session_id"]
    status, body = handle_api(
        web_service,
        "/api/act",
        {"session_id": sid, "action": "select_briefcase", "params": {"number": 10}},
    )
    assert status == 200
    assert body["view"]["status"] == "IN_PROGRESS"


def test_act_on_unknown_session_is_404(web_service: SessionService) -> None:
    status, body = handle_api(
        web_service,
        "/api/act",
        {"session_id": "nope", "action": "select_briefcase", "params": {"number": 1}},
    )
    assert status == 404
    assert "error" in body


def test_unknown_path_is_404(web_service: SessionService) -> None:
    status, _ = handle_api(web_service, "/api/nope", {})
    assert status == 404
