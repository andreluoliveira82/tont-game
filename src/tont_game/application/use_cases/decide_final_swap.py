"""DecideFinalSwap: the endgame decision to swap (or not) the final briefcase.

Single endgame use case. It orchestrates the domain primitives — first the
optional swap, then the reveal that finishes the game — and only after the
domain operation succeeds does it record the official result (ADR 0006:
validate/execute in the domain first, record the fact afterwards).
"""

from tont_game.application.game_session import GameSession
from tont_game.domain.clock import Clock
from tont_game.domain.history.records import OfficialResult


class DecideFinalSwap:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(self, session: GameSession, swap: bool) -> None:
        state = session.game_state
        record = session.game_record

        # The originally chosen briefcase (captured before any swap).
        original_briefcase = state.player_briefcase

        # Domain first: these validate FINAL_SWAP_PENDING and raise on misuse,
        # so an invalid state never reaches the history below.
        if swap:
            state.apply_final_swap()
        final_value = state.reveal_final_and_finish()

        assert original_briefcase is not None
        final_briefcase = state.player_briefcase
        assert final_briefcase is not None

        record.close(
            OfficialResult.from_final_reveal(
                swap_decision=swap,
                player_briefcase_value=original_briefcase.value,
                final_briefcase_number=final_briefcase.number,
                final_briefcase_value=final_value,
            ),
            self._clock.now(),
        )
