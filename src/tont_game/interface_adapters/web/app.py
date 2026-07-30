"""Pure request routing for the web adapter (no HTTP machinery).

Maps a JSON request to a call on the ``SessionService`` and back to a JSON-ready
response. Kept free of sockets so it can be tested directly; ``server`` wires it
to the standard-library HTTP server.
"""

from typing import Any

from tont_game.interface_adapters.web.session_service import (
    SessionService,
    UnknownSessionError,
)


def handle_api(
    service: SessionService, path: str, payload: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    if path == "/api/start":
        return 200, _start(service, payload)
    if path == "/api/act":
        return _act(service, payload)
    return 404, {"error": "not found"}


def _start(service: SessionService, payload: dict[str, Any]) -> dict[str, Any]:
    session_id, view = service.start(_coerce_seed(payload.get("seed")))
    return {"session_id": session_id, "view": view}


def _act(
    service: SessionService, payload: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    session_id = payload.get("session_id", "")
    action = payload.get("action", "")
    params = payload.get("params") or {}
    try:
        view = service.act(session_id, action, params)
    except UnknownSessionError:
        return 404, {"error": "unknown session"}
    return 200, {"view": view}


def _coerce_seed(seed: Any) -> int | None:
    if seed is None:
        return None
    try:
        return int(seed)
    except (TypeError, ValueError):
        return None
