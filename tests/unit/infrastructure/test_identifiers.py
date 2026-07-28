"""Unit tests for the UuidGameIdGenerator adapter."""

from uuid import UUID

from tont_game.domain.identifiers import GameIdGenerator
from tont_game.infrastructure.identifiers import UuidGameIdGenerator


def test_satisfies_protocol() -> None:
    assert isinstance(UuidGameIdGenerator(), GameIdGenerator)


def test_generates_unique_uuids() -> None:
    generator = UuidGameIdGenerator()
    first = generator.new_id()
    second = generator.new_id()
    assert isinstance(first, UUID)
    assert isinstance(second, UUID)
    assert first != second
