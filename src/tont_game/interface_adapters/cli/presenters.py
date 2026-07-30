"""Presenters: pure functions that format domain data as PT-BR text.

No I/O and no business rules here — only presentation. Money is formatted in
the Brazilian style (e.g. ``R$ 1.000.000,00``) without relying on ``locale``.
"""

from collections.abc import Sequence

from tont_game.domain.entities.briefcase import Briefcase
from tont_game.domain.errors import (
    BriefcaseAlreadyOpenedError,
    DomainError,
    InvalidBriefcaseNumberError,
    PlayerBriefcaseProtectedError,
    RoundLimitExceededError,
)
from tont_game.domain.history.records import Decision, EndingType, OfficialResult
from tont_game.domain.history.repository import (
    GameHistoryDetail,
    GameHistorySummary,
)
from tont_game.domain.simulation.post_game_simulation import SimulationResult
from tont_game.domain.value_objects.money import Money


def _group_thousands(digits: str) -> str:
    groups = []
    while len(digits) > 3:
        groups.append(digits[-3:])
        digits = digits[:-3]
    groups.append(digits)
    return ".".join(reversed(groups))


def format_money(money: Money) -> str:
    """Format money in Brazilian style, e.g. ``R$ 1.000,00``."""
    integer_part, _, decimals = f"{money.amount:.2f}".partition(".")
    return f"R$ {_group_thousands(integer_part)},{decimals}"


def welcome() -> str:
    return (
        "Bem-vindo ao Topa ou Não Topa!\n"
        "Escolha a sua maleta: ela será sua e ficará protegida até o final da partida."
    )


def seed_notice(seed: int) -> str:
    return f"Seed da partida: {seed}"


def player_briefcase(number: int) -> str:
    return f"Sua maleta é a de número {number}."


def round_header(round_number: int) -> str:
    return f"\n--- Rodada {round_number} ---"


def status_line(
    round_number: int,
    player_number: int,
    closed_count: int,
    remaining: Sequence[Money],
) -> str:
    """Compact one-line summary of the current game state."""
    ordered = sorted(remaining)
    span = f"{format_money(ordered[0])} a {format_money(ordered[-1])}"
    return (
        f"Rodada {round_number} | Sua maleta: {player_number} | "
        f"{closed_count} fechadas | Valores: {span}"
    )


def available_briefcases(numbers: Sequence[int]) -> str:
    listed = ", ".join(str(number) for number in sorted(numbers))
    return f"Maletas disponíveis: {listed}"


def remaining_values(values: Sequence[Money]) -> str:
    """Full, clear list of the values still in play (used when few remain)."""
    listed = " · ".join(format_money(value) for value in sorted(values))
    return f"Valores em jogo: {listed}"


def opened_briefcase(briefcase: Briefcase) -> str:
    return f"Maleta {briefcase.number} aberta: {format_money(briefcase.value)}."


_DECISION_RULE = "─" * 44
_VALUES_PER_LINE = 4


def _values_in_lines(values: Sequence[Money]) -> str:
    formatted = [format_money(value) for value in sorted(values)]
    lines = [
        " · ".join(formatted[start : start + _VALUES_PER_LINE])
        for start in range(0, len(formatted), _VALUES_PER_LINE)
    ]
    return "\n".join(lines)


def decision_block(
    offer_value: Money,
    round_number: int,
    remaining: Sequence[Money],
    player_number: int,
    closed_count: int,
) -> str:
    """Everything the player needs to decide Topa/Não Topa, in one block.

    Shows the offer, the full list of remaining values (sorted, grouped in
    readable lines) with their count, the player's briefcase and how many
    briefcases are still closed.
    """
    return (
        f"{_DECISION_RULE}\n"
        f"OFERTA DO BANQUEIRO (rodada {round_number}) — {format_money(offer_value)}\n"
        f"\n"
        f"Valores ainda em jogo ({len(remaining)}):\n"
        f"{_values_in_lines(remaining)}\n"
        f"\n"
        f"Sua maleta: {player_number} · Maletas fechadas: {closed_count}\n"
        f"{_DECISION_RULE}"
    )


def endgame_intro() -> str:
    return "\nRestam duas maletas: a sua e a última maleta fechada."


def endgame_reveal(
    original_number: int,
    original_value: Money,
    other_number: int,
    other_value: Money,
    swapped: bool,
) -> str:
    """Reveal both final briefcases and the outcome of the swap decision."""
    if swapped:
        return (
            f"Você trocou a maleta {original_number} pela maleta {other_number}.\n"
            f"Você levou {format_money(other_value)}.\n"
            f"A maleta que você deixou (maleta {original_number}) "
            f"tinha {format_money(original_value)}."
        )
    return (
        f"Você ficou com a maleta {original_number} "
        f"e levou {format_money(original_value)}.\n"
        f"A última maleta (maleta {other_number}) tinha {format_money(other_value)}."
    )


def official_result(result: OfficialResult) -> str:
    received = format_money(result.amount_received)
    real = format_money(result.player_briefcase_value)
    if result.ending_type is EndingType.OFFER_ACCEPTED:
        return f"Você TOPOU e recebe {received}. (A sua maleta valia {real}.)"
    if result.ending_type is EndingType.FINAL_REVEAL_WITH_SWAP:
        return (
            f"Você trocou de maleta e leva {received}. "
            f"(A sua maleta original valia {real}.)"
        )
    return f"Você ficou com a sua maleta e leva {received}."


def simulation_comparison(simulation: SimulationResult) -> str:
    official = format_money(simulation.official_amount)
    hypothetical = format_money(simulation.hypothetical_amount)
    difference = format_money(simulation.absolute_difference())
    if simulation.hypothetical_amount == simulation.official_amount:
        verdict = "Daria no mesmo."
    elif simulation.hypothetical_is_higher():
        verdict = "Você teria ganhado mais se tivesse continuado."
    else:
        verdict = "Você fez bem em aceitar a oferta."
    return (
        f"Resultado oficial:     {official}\n"
        f"Resultado hipotético:  {hypothetical}\n"
        f"Diferença:             {difference}\n"
        f"{verdict}"
    )


def history_saved() -> str:
    return "Partida registrada no seu histórico."


def history_save_failed() -> str:
    return "Não foi possível registrar esta partida no histórico."


_ENDING_LABELS = {
    EndingType.OFFER_ACCEPTED: "Topa",
    EndingType.FINAL_REVEAL_WITH_SWAP: "Troca final",
    EndingType.FINAL_REVEAL_WITHOUT_SWAP: "Sem troca",
}


def history_empty() -> str:
    return "Você ainda não tem partidas no histórico."


def history_list(summaries: Sequence[GameHistorySummary]) -> str:
    """List past games, most recent first (one line each)."""
    lines = [f"Seu histórico ({len(summaries)} partida(s)):"]
    for summary in summaries:
        when = summary.finished_at.strftime("%d/%m/%Y %H:%M")
        label = _ENDING_LABELS.get(summary.ending_type, summary.ending_type.value)
        lines.append(
            f"- {when} · {label} · levou {format_money(summary.amount_received)}"
        )
    return "\n".join(lines)


def history_unavailable() -> str:
    return "Não foi possível ler o seu histórico agora."


def history_unknown_subcommand(name: str) -> str:
    return f"Subcomando de histórico desconhecido: {name}"


def history_show_usage() -> str:
    return "Uso: tont-game history show <id>"


def history_invalid_id(raw_id: str) -> str:
    return f"Identificador de partida inválido: {raw_id}"


def history_not_found() -> str:
    return "Partida não encontrada no seu histórico."


_DECISION_LABELS = {Decision.ACCEPT: "Topa", Decision.REJECT: "Não Topa"}


def history_detail(detail: GameHistoryDetail) -> str:
    """Full, readable view of a single persisted game."""
    when = detail.finished_at.strftime("%d/%m/%Y %H:%M") if detail.finished_at else "—"
    label = _ENDING_LABELS.get(detail.ending_type, detail.ending_type.value)
    seed = f" · seed {detail.seed}" if detail.seed is not None else ""
    lines = [
        f"Partida {detail.game_id}",
        f"Encerrada em {when}{seed}",
        f"Sua maleta: {detail.player_briefcase} "
        f"(valia {format_money(detail.player_briefcase_value)})",
        f"Desfecho: {label} · você levou {format_money(detail.amount_received)}",
    ]
    if detail.rounds:
        lines.append("Rodadas:")
        for round_detail in detail.rounds:
            opened = (
                ", ".join(
                    f"{number} ({format_money(value)})"
                    for number, value in round_detail.openings
                )
                or "—"
            )
            offer = format_money(round_detail.offer) if round_detail.offer else "—"
            decision = _DECISION_LABELS.get(round_detail.decision, "—")
            lines.append(
                f"- Rodada {round_detail.round_number}: abriu {opened} "
                f"· oferta {offer} · {decision}"
            )
    return "\n".join(lines)


def help_text() -> str:
    """Top-level CLI help covering the whole public command surface."""
    return (
        "tont-game — Topa ou Não Topa (CLI)\n"
        "\n"
        "Uso:\n"
        "  tont-game [SEED]           Joga uma partida (SEED opcional)\n"
        "  tont-game history          Lista suas partidas anteriores\n"
        "  tont-game history show ID  Detalha uma partida pelo id\n"
        "  tont-game --version        Mostra a versão\n"
        "  tont-game --help           Mostra esta ajuda"
    )


def version_line(version: str) -> str:
    return f"tont-game {version}"


def history_usage() -> str:
    return (
        "Uso do histórico:\n"
        "  tont-game history          Lista suas partidas anteriores\n"
        "  tont-game history show ID  Detalha uma partida pelo id"
    )


def aborted() -> str:
    return "\nPartida encerrada. Até a próxima!"


def error_message(error: DomainError) -> str:
    """Map a domain error to a PT-BR message for the player."""
    if isinstance(error, InvalidBriefcaseNumberError):
        return "Maleta inexistente. Escolha um número válido."
    if isinstance(error, BriefcaseAlreadyOpenedError):
        return "Essa maleta já foi aberta. Escolha outra."
    if isinstance(error, PlayerBriefcaseProtectedError):
        return "Você não pode abrir a sua própria maleta. Escolha outra."
    if isinstance(error, RoundLimitExceededError):
        return "Você já abriu todas as maletas permitidas nesta rodada."
    return "Operação inválida neste momento."
