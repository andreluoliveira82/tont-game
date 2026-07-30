"""Component tests for the CLI history command (Phase 11)."""

from datetime import UTC, datetime
from uuid import uuid4

from tont_game.domain.history.records import EndingType
from tont_game.domain.history.repository import GameHistorySummary
from tont_game.domain.value_objects.money import Money


def a_summary(amount: str = "120.50") -> GameHistorySummary:
    return GameHistorySummary(
        game_id=uuid4(),
        finished_at=datetime(2026, 7, 29, 10, tzinfo=UTC),
        ending_type=EndingType.OFFER_ACCEPTED,
        amount_received=Money.of(amount),
        player_briefcase_value=Money.of("250"),
    )


def test_empty_history_is_reported(run_history) -> None:
    console = run_history([])
    assert "ainda não tem partidas" in console.text


def test_history_lists_saved_games(run_history) -> None:
    console = run_history([a_summary("120.50"), a_summary("1000")])
    assert "Seu histórico (2 partida(s)):" in console.text
    assert "R$ 120,50" in console.text
    assert "R$ 1.000,00" in console.text


def test_history_read_failure_degrades_gracefully(run_history) -> None:
    console = run_history(failing=True)
    assert "Não foi possível ler" in console.text
