"""Unit tests for the Briefcase entity."""

import pytest

from tont_game.domain.entities.briefcase import Briefcase
from tont_game.domain.errors import BriefcaseAlreadyOpenedError
from tont_game.domain.value_objects.money import Money


def test_briefcase_starts_closed() -> None:
    briefcase = Briefcase(number=1, value=Money.of("100"))
    assert briefcase.opened is False


def test_open_marks_briefcase_as_opened() -> None:
    briefcase = Briefcase(number=1, value=Money.of("100"))
    briefcase.open()
    assert briefcase.opened is True


def test_opening_twice_raises() -> None:
    briefcase = Briefcase(number=1, value=Money.of("100"))
    briefcase.open()
    with pytest.raises(BriefcaseAlreadyOpenedError):
        briefcase.open()


def test_briefcase_rejects_non_positive_number() -> None:
    with pytest.raises(ValueError):
        Briefcase(number=0, value=Money.of("100"))


def test_briefcase_rejects_non_money_value() -> None:
    with pytest.raises(TypeError):
        Briefcase(number=1, value=100)  # type: ignore[arg-type]
