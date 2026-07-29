"""Unit tests for the CLI presenters (pure PT-BR formatting)."""

from tont_game.domain.entities.briefcase import Briefcase
from tont_game.domain.errors import (
    BriefcaseAlreadyOpenedError,
    InvalidBriefcaseNumberError,
    InvalidGameStateError,
    PlayerBriefcaseProtectedError,
    RoundLimitExceededError,
)
from tont_game.domain.history.records import OfficialResult
from tont_game.domain.simulation.post_game_simulation import (
    SimulationResult,
    SimulationScenario,
)
from tont_game.domain.value_objects.money import Money
from tont_game.interface_adapters.cli import presenters


def test_format_money_zero() -> None:
    assert presenters.format_money(Money.of(0)) == "R$ 0,00"


def test_format_money_cents() -> None:
    assert presenters.format_money(Money.of("0.50")) == "R$ 0,50"
    assert presenters.format_money(Money.of("1234.5")) == "R$ 1.234,50"


def test_format_money_thousands_and_millions() -> None:
    assert presenters.format_money(Money.of("1000")) == "R$ 1.000,00"
    assert presenters.format_money(Money.of("1000000")) == "R$ 1.000.000,00"
    assert presenters.format_money(Money.of("2000000")) == "R$ 2.000.000,00"


def test_round_header_and_offer() -> None:
    assert presenters.round_header(3) == "--- Rodada 3 ---"
    assert presenters.offer(Money.of("100"), 3) == (
        "Oferta do Banqueiro (rodada 3): R$ 100,00."
    )


def test_remaining_and_eliminated_values() -> None:
    remaining = presenters.remaining_values([Money.of("50"), Money.of("10")])
    assert remaining == "Valores ainda em jogo: R$ 10,00, R$ 50,00"
    assert presenters.eliminated_values([]) == "Valores eliminados: (nenhum ainda)"
    opened = [Briefcase(1, Money.of("5"), opened=True)]
    assert presenters.eliminated_values(opened) == "Valores eliminados: R$ 5,00"


def test_official_result_topa() -> None:
    result = OfficialResult.from_accepted_offer(
        decision_round=2,
        accepted_offer=Money.of("100"),
        player_briefcase_value=Money.of("250"),
    )
    text = presenters.official_result(result)
    assert "TOPOU" in text
    assert "R$ 100,00" in text
    assert "R$ 250,00" in text


def test_official_result_endgame_with_and_without_swap() -> None:
    with_swap = OfficialResult.from_final_reveal(
        swap_decision=True,
        player_briefcase_value=Money.of("50"),
        final_briefcase_number=13,
        final_briefcase_value=Money.of("500"),
    )
    assert "trocou" in presenters.official_result(with_swap)
    assert "R$ 500,00" in presenters.official_result(with_swap)

    without_swap = OfficialResult.from_final_reveal(
        swap_decision=False,
        player_briefcase_value=Money.of("500"),
        final_briefcase_number=7,
        final_briefcase_value=Money.of("500"),
    )
    assert "ficou com a sua maleta" in presenters.official_result(without_swap)


def test_simulation_comparison() -> None:
    simulation = SimulationResult(
        scenario=SimulationScenario.CONTINUE_HOLD,
        hypothetical_amount=Money.of("250"),
        official_amount=Money.of("100"),
    )
    text = presenters.simulation_comparison(simulation)
    assert "Resultado oficial:" in text
    assert "R$ 100,00" in text
    assert "Resultado hipotético:" in text
    assert "R$ 250,00" in text
    assert "R$ 150,00" in text  # absolute difference
    assert "teria ganhado mais" in text


def test_error_messages_are_localized() -> None:
    assert "inexistente" in presenters.error_message(InvalidBriefcaseNumberError())
    assert "já foi aberta" in presenters.error_message(BriefcaseAlreadyOpenedError())
    assert "sua própria maleta" in presenters.error_message(
        PlayerBriefcaseProtectedError()
    )
    assert "nesta rodada" in presenters.error_message(RoundLimitExceededError())
    assert "inválida" in presenters.error_message(InvalidGameStateError())
