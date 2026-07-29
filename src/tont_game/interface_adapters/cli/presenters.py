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
from tont_game.domain.history.records import EndingType, OfficialResult
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
    return "Bem-vindo ao Topa ou Não Topa!"


def player_briefcase(number: int) -> str:
    return f"Sua maleta é a de número {number}."


def round_header(round_number: int) -> str:
    return f"--- Rodada {round_number} ---"


def remaining_values(values: Sequence[Money]) -> str:
    formatted = ", ".join(format_money(value) for value in sorted(values))
    return f"Valores ainda em jogo: {formatted}"


def eliminated_values(opened: Sequence[Briefcase]) -> str:
    if not opened:
        return "Valores eliminados: (nenhum ainda)"
    values = sorted(briefcase.value for briefcase in opened)
    formatted = ", ".join(format_money(value) for value in values)
    return f"Valores eliminados: {formatted}"


def opened_briefcase(briefcase: Briefcase) -> str:
    return f"Maleta {briefcase.number} aberta: {format_money(briefcase.value)}."


def offer(offer_value: Money, round_number: int) -> str:
    return f"Oferta do Banqueiro (rodada {round_number}): {format_money(offer_value)}."


def endgame_intro() -> str:
    return "Restam duas maletas: a sua e a última maleta fechada."


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
