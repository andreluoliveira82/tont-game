"""Shared deterministic doubles and fixtures for the web adapter tests.

Identity shuffle → briefcase ``i`` holds the ``i``-th official value.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4

import pytest

from tont_game.domain.services.banker import DefaultBankerStrategy
from tont_game.interface_adapters.web.session_service import SessionService

T = TypeVar("T")


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 30, tzinfo=UTC)


class FakeIdGenerator:
    def new_id(self) -> UUID:
        return uuid4()


class IdentityRandomSource:
    def shuffle(self, items: Sequence[T]) -> list[T]:
        return list(items)


def make_web_service() -> SessionService:
    return SessionService(
        clock=FakeClock(),
        id_generator=FakeIdGenerator(),
        banker_strategy=DefaultBankerStrategy(),
        make_random_source=lambda seed: IdentityRandomSource(),
    )


@pytest.fixture
def web_service() -> SessionService:
    return make_web_service()
