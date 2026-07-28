"""Unit tests for the SystemClock adapter."""

from datetime import datetime

from tont_game.domain.clock import Clock
from tont_game.infrastructure.clock import SystemClock


def test_satisfies_clock_protocol() -> None:
    assert isinstance(SystemClock(), Clock)


def test_now_returns_timezone_aware_utc_datetime() -> None:
    now = SystemClock().now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.utcoffset() is not None
    assert now.utcoffset().total_seconds() == 0
