"""Component tests for the CLI controller driven by a scripted FakeConsole.

Uses the identity random source (see conftest): with the official values,
briefcase ``i`` holds the ``i``-th official value. The player picks briefcase
10 (worth R$ 500,00); the last remaining briefcase is 26 (R$ 2.000.000,00).
The ``run_cli`` fixture builds and runs the controller and returns the console.
"""

from tont_game.interface_adapters.cli import narration
from tont_game.interface_adapters.cli.narration import EndingMoment

# Briefcase numbers the player may open (all but the chosen briefcase 10).
OPENABLE = [n for n in range(1, 27) if n != 10]
QUOTAS = [6, 5, 4, 3, 2, 1, 1, 1, 1]


def reject_all_inputs(swap_answer: str) -> list[str]:
    inputs = ["10"]
    index = 0
    for quota in QUOTAS:
        for _ in range(quota):
            inputs.append(str(OPENABLE[index]))
            index += 1
        inputs.append("n")  # reject the offer
    inputs.append(swap_answer)  # endgame swap decision
    return inputs


def topa_round_one_inputs(simulate_answer: str, *, decision: str = "t") -> list[str]:
    return ["10", "1", "2", "3", "4", "5", "6", decision, simulate_answer]


def endgame_inputs(player: int, leave: int, swap_answer: str) -> list[str]:
    """Reject every offer up to the endgame, leaving briefcase ``leave`` closed.

    With the identity shuffle, briefcase ``i`` holds the ``i``-th official value,
    so ``player`` and ``leave`` fully determine the two final briefcase values.
    """
    to_open = [n for n in range(1, 27) if n not in (player, leave)]
    inputs = [str(player)]
    index = 0
    for quota in QUOTAS:
        for _ in range(quota):
            inputs.append(str(to_open[index]))
            index += 1
        inputs.append("n")  # reject the offer
    inputs.append(swap_answer)
    return inputs


def test_topa_flow_presents_official_result(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    assert "Bem-vindo" in console.text
    assert "Sua maleta é a de número 10." in console.text
    assert "--- Rodada 1 ---" in console.text
    assert "OFERTA DO BANQUEIRO (rodada 1)" in console.text
    assert "TOPOU" in console.text


def test_round_shows_status_and_available_briefcases(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    assert "Rodada 1 | Sua maleta: 10" in console.text
    assert "Maletas disponíveis:" in console.text


def test_decision_block_lists_all_values_even_in_early_round(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    # Round 1 decision: 6 opened, 20 values still in play — all listed.
    assert "Valores ainda em jogo (20):" in console.text
    # A high value that was not opened is shown before the decision.
    assert "R$ 2.000.000,00" in console.text


def test_offer_is_not_duplicated_in_the_decision(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    assert console.text.count("OFERTA DO BANQUEIRO") == 1


def test_topa_accepts_sim_alias(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n", decision="sim"))
    assert "TOPOU" in console.text


def test_topa_then_simulation_shows_comparison(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("s"))
    assert "TOPOU" in console.text
    assert "Resultado oficial:" in console.text
    assert "Resultado hipotético:" in console.text
    # The player's own briefcase (10) is worth R$ 500,00 (the hypothetical).
    assert "R$ 500,00" in console.text


def test_endgame_without_swap_reveals_both_briefcases(run_cli) -> None:
    console = run_cli(reject_all_inputs("n"))
    assert "Restam duas maletas" in console.text
    assert "ficou com a maleta 10" in console.text
    assert "R$ 500,00" in console.text  # kept briefcase 10
    # The other (last) briefcase is 26 (R$ 2.000.000,00) and is now revealed.
    assert "última maleta (maleta 26)" in console.text
    assert "R$ 2.000.000,00" in console.text


def test_endgame_with_swap_reveals_both_briefcases(run_cli) -> None:
    console = run_cli(reject_all_inputs("s"))
    assert "trocou a maleta 10 pela maleta 26" in console.text
    assert "levou R$ 2.000.000,00" in console.text
    assert "deixou (maleta 10) tinha R$ 500,00" in console.text


def test_non_integer_input_reprompts(run_cli) -> None:
    console = run_cli(["abc", *topa_round_one_inputs("n")])
    assert "Entrada inválida. Digite um número." in console.text
    assert "TOPOU" in console.text


def test_invalid_briefcase_number_reprompts(run_cli) -> None:
    console = run_cli(["10", "99", "1", "2", "3", "4", "5", "6", "t", "n"])
    assert "Maleta inexistente" in console.text
    assert "TOPOU" in console.text


def test_cannot_open_player_briefcase_reprompts(run_cli) -> None:
    console = run_cli(["10", "10", "1", "2", "3", "4", "5", "6", "t", "n"])
    assert "sua própria maleta" in console.text
    assert "TOPOU" in console.text


def test_cannot_open_already_opened_briefcase_reprompts(run_cli) -> None:
    console = run_cli(["10", "1", "1", "2", "3", "4", "5", "6", "t", "n"])
    assert "já foi aberta" in console.text
    assert "TOPOU" in console.text


def test_invalid_decision_reprompts(run_cli) -> None:
    console = run_cli(["10", "1", "2", "3", "4", "5", "6", "maybe", "t", "n"])
    assert "Digite Topa (t) ou Não Topa (n)." in console.text
    assert "TOPOU" in console.text


def test_seed_is_echoed_when_provided(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"), seed=42)
    assert "Seed da partida: 42" in console.text


class _EofConsole:
    def __init__(self) -> None:
        self.outputs: list[str] = []

    def write(self, text: str) -> None:
        self.outputs.append(text)

    def read_line(self, prompt: str) -> str:
        raise EOFError


class _InterruptConsole:
    def __init__(self) -> None:
        self.outputs: list[str] = []

    def write(self, text: str) -> None:
        self.outputs.append(text)

    def read_line(self, prompt: str) -> str:
        raise KeyboardInterrupt


def test_topa_triumph_narration_follows_the_factual_line(run_cli) -> None:
    # Player keeps briefcase 10 (R$ 500,00); the round-1 offer dwarfs it.
    console = run_cli(topa_round_one_inputs("n"))
    line = narration.messages(EndingMoment.TRIUMPH)[0]
    assert line in console.text
    assert console.text.index("TOPOU") < console.text.index(line)


def test_topa_regret_narration_is_shown(run_cli) -> None:
    # Player keeps briefcase 26 (R$ 2.000.000,00); the accepted offer is far less.
    console = run_cli(["26", "1", "2", "3", "4", "5", "6", "t", "n"])
    assert narration.messages(EndingMoment.REGRET)[0] in console.text


def test_topa_close_result_stays_silent(run_cli) -> None:
    # Player keeps briefcase 20 (R$ 100.000,00), close to the offer: no narration.
    console = run_cli(["20", "1", "2", "3", "4", "5", "6", "t", "n"])
    every_message = [
        text for moment in EndingMoment for text in narration.messages(moment)
    ]
    assert not any(text in console.text for text in every_message)


def test_topa_narration_is_deterministic(run_cli) -> None:
    first = run_cli(topa_round_one_inputs("n")).text
    second = run_cli(topa_round_one_inputs("n")).text
    assert first == second


def test_endgame_swap_triumph_narration_follows_the_factual_line(run_cli) -> None:
    # Swap R$ 0,50 (briefcase 1) for R$ 100,00 (briefcase 8): took much more.
    console = run_cli(endgame_inputs(player=1, leave=8, swap_answer="s"))
    line = narration.messages(EndingMoment.TRIUMPH)[0]
    assert line in console.text
    assert console.text.index("trocou a maleta") < console.text.index(line)


def test_endgame_swap_regret_narration_is_shown(run_cli) -> None:
    # Swap R$ 1.000.000,00 (briefcase 24) for R$ 100,00 (briefcase 8): took far less.
    console = run_cli(endgame_inputs(player=24, leave=8, swap_answer="s"))
    assert narration.messages(EndingMoment.REGRET)[0] in console.text


def test_endgame_no_swap_peak_narration_is_shown(run_cli) -> None:
    # Keep briefcase 26 (R$ 2.000.000,00): the biggest prize on the table.
    console = run_cli(endgame_inputs(player=26, leave=1, swap_answer="n"))
    assert narration.messages(EndingMoment.PEAK)[0] in console.text


def test_endgame_no_swap_floor_narration_is_shown(run_cli) -> None:
    # Keep briefcase 1 (R$ 0,50): the smallest prize on the table.
    console = run_cli(endgame_inputs(player=1, leave=26, swap_answer="n"))
    assert narration.messages(EndingMoment.FLOOR)[0] in console.text


def test_endgame_close_result_stays_silent(run_cli) -> None:
    # Keep R$ 75,00 (briefcase 7) with R$ 100,00 (briefcase 8) left: too close.
    console = run_cli(endgame_inputs(player=7, leave=8, swap_answer="n"))
    every_message = [
        text for moment in EndingMoment for text in narration.messages(moment)
    ]
    assert not any(text in console.text for text in every_message)


def test_endgame_narration_is_deterministic(run_cli) -> None:
    first = run_cli(endgame_inputs(player=1, leave=8, swap_answer="s")).text
    second = run_cli(endgame_inputs(player=1, leave=8, swap_answer="s")).text
    assert first == second


def test_finished_game_is_saved_to_history(run_cli, fake_history_repo) -> None:
    console = run_cli(topa_round_one_inputs("n"), history_repository=fake_history_repo)
    assert len(fake_history_repo.saved) == 1
    assert fake_history_repo.saved[0].official_result is not None
    assert "registrada no seu histórico" in console.text


def test_history_save_failure_degrades_gracefully(
    run_cli, failing_history_repo
) -> None:
    console = run_cli(
        topa_round_one_inputs("n"), history_repository=failing_history_repo
    )
    assert "Não foi possível registrar" in console.text
    assert "TOPOU" in console.text  # the game still completed normally


def test_without_repository_there_is_no_history_line(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    assert "histórico" not in console.text


def test_eof_ends_gracefully(make_controller) -> None:
    console = _EofConsole()
    make_controller(console).run()
    assert "Partida encerrada" in "\n".join(console.outputs)


def test_keyboard_interrupt_ends_gracefully(make_controller) -> None:
    console = _InterruptConsole()
    make_controller(console).run()
    assert "Partida encerrada" in "\n".join(console.outputs)
