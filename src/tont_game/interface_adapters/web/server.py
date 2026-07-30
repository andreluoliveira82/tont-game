"""Standard-library HTTP server for the web adapter (composition root).

No framework, no dependencies. Serves a single page and a tiny JSON API that
drives the existing use cases via ``SessionService``. Run with:

    python -m tont_game.interface_adapters.web.server
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.infrastructure.clock import SystemClock
from tont_game.infrastructure.identifiers import UuidGameIdGenerator
from tont_game.infrastructure.randomness.random_source import DefaultRandomSource
from tont_game.interface_adapters.web.app import handle_api
from tont_game.interface_adapters.web.session_service import SessionService

_INDEX = Path(__file__).parent / "static" / "index.html"


def _build_service() -> SessionService:
    return SessionService(
        clock=SystemClock(),
        id_generator=UuidGameIdGenerator(),
        banker_strategy=DefaultBankerStrategy(),
        make_random_source=lambda seed: DefaultRandomSource(seed),
    )


def _make_handler(service: SessionService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path in ("/", "/index.html"):
                self._send_bytes(200, _INDEX.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid json"})
                return
            status, body = handle_api(service, self.path, payload)
            self._send_json(status, body)

        def log_message(self, *args: object) -> None:  # silence default logging
            pass

        def _send_json(self, status: int, body: dict) -> None:
            self._send_bytes(
                status,
                json.dumps(body).encode("utf-8"),
                "application/json; charset=utf-8",
            )

        def _send_bytes(self, status: int, data: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), _make_handler(_build_service()))
    print(f"tont-game (web) em http://{host}:{port} — Ctrl+C para encerrar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
