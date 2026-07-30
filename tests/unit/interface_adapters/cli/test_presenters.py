"""Unit tests for the CLI presenters (pure PT-BR formatting)."""

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


def test_welcome_orients_the_player() -> None:
    text = presenters.welcome()
    assert "Bem-vindo" in text
    assert "protegida" in text


def test_seed_notice() -> None:
    assert presenters.seed_notice(42) == "Seed da partida: 42"


def test_round_header() -> None:
    assert "--- Rodada 3 ---" in presenters.round_header(3)


def test_decision_block_gathers_everything_for_the_decision() -> None:
    remaining = [
        Money.of("500000"),
        Money.of("100"),
        Money.of("10000"),
        Money.of("1000000"),
        Money.of("25000"),
        Money.of("500"),
    ]
    block = presenters.decision_block(
        offer_value=Money.of("405616"),
        round_number=6,
        remaining=remaining,
        player_number=20,
        closed_count=6,
    )
    # Offer highlighted, once, with the round.
    assert "OFERTA DO BANQUEIRO (rodada 6) — R$ 405.616,00" in block
    assert block.count("OFERTA DO BANQUEIRO") == 1
    # Count and the full, sorted list of values (all present).
    assert "Valores ainda em jogo (6):" in block
    for value in remaining:
        assert presenters.format_money(value) in block
    values_section = block.split("Valores ainda em jogo (6):\n", 1)[1]
    listed = [
        token.strip()
        for line in values_section.splitlines()
        for token in line.split("·")
        if token.strip().startswith("R$")
    ]
    assert listed == [presenters.format_money(v) for v in sorted(remaining)]
    # Player briefcase and closed count.
    assert "Sua maleta: 20" in block
    assert "Maletas fechadas: 6" in block


def test_decision_block_wraps_many_values_into_multiple_lines() -> None:
    remaining = [Money.of(n) for n in range(1, 21)]  # 20 values (early round)
    block = presenters.decision_block(
        offer_value=Money.of("100"),
        round_number=1,
        remaining=remaining,
        player_number=10,
        closed_count=20,
    )
    assert "Valores ainda em jogo (20):" in block
    for value in remaining:
        assert presenters.format_money(value) in block
    # 20 values at 4 per line -> the values section spans several lines.
    values_section = block.split("Valores ainda em jogo (20):\n", 1)[1]
    value_lines = [
        line for line in values_section.splitlines() if line.strip().startswith("R$")
    ]
    assert len(value_lines) == 5


def test_status_line_is_compact() -> None:
    line = presenters.status_line(
        round_number=7,
        player_number=14,
        closed_count=5,
        remaining=[Money.of("10"), Money.of("2000000"), Money.of("50000")],
    )
    assert "Rodada 7" in line
    assert "Sua maleta: 14" in line
    assert "5 fechadas" in line
    assert "R$ 10,00 a R$ 2.000.000,00" in line


def test_available_briefcases_lists_sorted_numbers() -> None:
    assert presenters.available_briefcases([8, 2, 5]) == "Maletas disponíveis: 2, 5, 8"


def test_remaining_values_full_list() -> None:
    text = presenters.remaining_values([Money.of("50"), Money.of("10")])
    assert text == "Valores em jogo: R$ 10,00 · R$ 50,00"


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


def test_endgame_reveal_without_swap() -> None:
    text = presenters.endgame_reveal(
        original_number=14,
        original_value=Money.of("500"),
        other_number=7,
        other_value=Money.of("2000000"),
        swapped=False,
    )
    assert "ficou com a maleta 14" in text
    assert "R$ 500,00" in text
    assert "última maleta (maleta 7)" in text
    assert "R$ 2.000.000,00" in text


def test_endgame_reveal_with_swap() -> None:
    text = presenters.endgame_reveal(
        original_number=14,
        original_value=Money.of("500"),
        other_number=7,
        other_value=Money.of("2000000"),
        swapped=True,
    )
    assert "trocou a maleta 14 pela maleta 7" in text
    assert "levou R$ 2.000.000,00" in text
    assert "deixou (maleta 14) tinha R$ 500,00" in text


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


def test_simulation_comparison_official_beats_hypothetical() -> None:
    simulation = SimulationResult(
        scenario=SimulationScenario.CONTINUE_HOLD,
        hypothetical_amount=Money.of("100"),
        official_amount=Money.of("250"),
    )
    text = presenters.simulation_comparison(simulation)
    assert "R$ 150,00" in text  # absolute difference
    assert "Você fez bem em aceitar a oferta." in text


def test_simulation_comparison_tie() -> None:
    simulation = SimulationResult(
        scenario=SimulationScenario.CONTINUE_HOLD,
        hypothetical_amount=Money.of("100"),
        official_amount=Money.of("100"),
    )
    text = presenters.simulation_comparison(simulation)
    assert "R$ 0,00" in text  # no difference
    assert "Daria no mesmo." in text


def test_help_text_covers_the_public_surface() -> None:
    text = presenters.help_text()
    assert "tont-game [SEED]" in text
    assert "history" in text
    assert "history show" in text
    assert "--version" in text
    assert "--help" in text


def test_version_line() -> None:
    assert presenters.version_line("1.3.0") == "tont-game 1.3.0"


def test_history_usage_lists_commands() -> None:
    text = presenters.history_usage()
    assert "history" in text
    assert "history show" in text


def test_aborted_message() -> None:
    assert "Partida encerrada" in presenters.aborted()


def test_error_messages_are_localized() -> None:
    assert "inexistente" in presenters.error_message(InvalidBriefcaseNumberError())
    assert "já foi aberta" in presenters.error_message(BriefcaseAlreadyOpenedError())
    assert "sua própria maleta" in presenters.error_message(
        PlayerBriefcaseProtectedError()
    )
    assert "nesta rodada" in presenters.error_message(RoundLimitExceededError())
    assert "inválida" in presenters.error_message(InvalidGameStateError())
