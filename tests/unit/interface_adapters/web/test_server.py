"""Smoke tests for the web server composition (Sprint 1)."""

from tont_game.interface_adapters.web import server
from tont_game.interface_adapters.web.session_service import SessionService


def test_index_page_exists_and_is_not_empty() -> None:
    assert server._INDEX.exists()
    assert server._INDEX.read_text(encoding="utf-8").strip()


def test_build_service_wires_a_session_service() -> None:
    assert isinstance(server._build_service(), SessionService)
