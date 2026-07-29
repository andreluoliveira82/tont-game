"""Ending narration: turns the facts of a finished game into an optional
emotional one-liner, shown after the factual result.

This is a presentation concern and stays pure. It only classifies the ending
moment from four monetary facts and holds the static message bank. It performs
no I/O, no randomness, and knows nothing about the controller, presenters,
game state, official result or history records. Picking a variant and writing
it are the caller's responsibility.

When no moment stands out, the silence is intentional: the factual result line
already closes the game on its own.
"""

from enum import Enum

from tont_game.domain.value_objects.money import Money


class EndingMoment(Enum):
    """The emotional moment an ending deserves, or none when it is unremarkable."""

    PEAK = "PEAK"  # APOGEU: took home the biggest prize on the table
    FLOOR = "FLOOR"  # FUNDO: took home the smallest prize on the table
    TRIUMPH = "TRIUMPH"  # VITÓRIA: took much more than the alternative
    REGRET = "REGRET"  # ARREPENDIMENTO: the alternative was worth much more


def moment_for(
    got: Money, gave_up: Money, max_value: Money, min_value: Money
) -> EndingMoment | None:
    """Classify the ending from what the player took home (``got``) versus the
    alternative they gave up (``gave_up``), and the game's ``max_value`` and
    ``min_value``.

    Precedence: PEAK over FLOOR over TRIUMPH over REGRET. "Much more" means at
    least the double. Anything short of that is silence (``None``).
    """
    if got == max_value:
        return EndingMoment.PEAK
    if got == min_value:
        return EndingMoment.FLOOR
    if got.amount >= gave_up.amount * 2:
        return EndingMoment.TRIUMPH
    if gave_up.amount >= got.amount * 2:
        return EndingMoment.REGRET
    return None


_MESSAGES: dict[EndingMoment, tuple[str, ...]] = {
    EndingMoment.PEAK: (
        "É o topo da mesa — não dá pra fazer melhor do que isso!",
        "O maior prêmio do jogo saiu com você. Simplesmente inacreditável!",
        "Chegou ao teto: nenhuma maleta valia mais do que a sua.",
    ),
    EndingMoment.FLOOR: (
        "O menor prêmio da mesa… mas você encarou o Banqueiro até o fim.",
        "A sorte ficou do outro lado desta vez. Cabeça erguida!",
        "Não foi o valor dos sonhos, mas a coragem foi toda sua.",
    ),
    EndingMoment.TRIUMPH: (
        "Que jogada! Você levou muito mais do que a alternativa.",
        "Instinto afiado: a sua escolha valeu — e valeu muito.",
        "Saiu ganhando com folga. Grande decisão!",
    ),
    EndingMoment.REGRET: (
        "A alternativa valia muito mais — dessa vez não deu.",
        "O grande prêmio ficou do outro lado.",
        "Escapou uma bela quantia bem debaixo do seu nariz.",
    ),
}


def messages(moment: EndingMoment) -> tuple[str, ...]:
    """Return the variant messages for a given ending moment."""
    return _MESSAGES[moment]
