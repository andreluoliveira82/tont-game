"""Component tests for the CLI controller driven by a scripted FakeConsole.

Uses the identity random source (see conftest): with the official values,
briefcase ``i`` holds the ``i``-th official value. The player picks briefcase
10 (worth R$ 500,00); the last remaining briefcase is 26 (R$ 2.000.000,00).
The ``run_cli`` fixture builds and runs the controller and returns the console.
"""

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


def topa_round_one_inputs(simulate_answer: str) -> list[str]:
    return ["10", "1", "2", "3", "4", "5", "6", "t", simulate_answer]


def test_topa_flow_presents_official_result(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("n"))
    assert "Bem-vindo" in console.text
    assert "Sua maleta é a de número 10." in console.text
    assert "--- Rodada 1 ---" in console.text
    assert "Oferta do Banqueiro (rodada 1)" in console.text
    assert "TOPOU" in console.text


def test_topa_then_simulation_shows_comparison(run_cli) -> None:
    console = run_cli(topa_round_one_inputs("s"))
    assert "TOPOU" in console.text
    assert "Resultado oficial:" in console.text
    assert "Resultado hipotético:" in console.text
    # The player's own briefcase (10) is worth R$ 500,00 (the hypothetical).
    assert "R$ 500,00" in console.text


def test_endgame_without_swap(run_cli) -> None:
    console = run_cli(reject_all_inputs("n"))
    assert "Restam duas maletas" in console.text
    assert "ficou com a sua maleta" in console.text
    assert "R$ 500,00" in console.text  # kept briefcase 10


def test_endgame_with_swap(run_cli) -> None:
    console = run_cli(reject_all_inputs("s"))
    assert "trocou de maleta" in console.text
    assert "R$ 2.000.000,00" in console.text  # swapped to briefcase 26


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
    assert "Resposta inválida. Digite 't' ou 'n'." in console.text
    assert "TOPOU" in console.text
