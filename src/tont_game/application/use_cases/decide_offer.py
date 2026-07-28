"""DecideOffer: the player accepts (Topa) or rejects (Não Topa) an offer."""

from tont_game.application.game_session import GameSession
from tont_game.domain.clock import Clock
from tont_game.domain.history.records import Decision, OfficialResult
from tont_game.domain.value_objects.game_status import GameStatus


class DecideOffer:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def execute(self, session: GameSession, decision: Decision) -> None:
        state = session.game_state
        record = session.game_record
        round_number = state.current_round

        if decision is Decision.ACCEPT:
            accepted_offer = state.accept_offer()
            player_briefcase = state.player_briefcase
            assert player_briefcase is not None  # game is in progress
            record.record_decision(round_number, Decision.ACCEPT)
            record.close(
                OfficialResult.from_accepted_offer(
                    decision_round=round_number,
                    accepted_offer=accepted_offer,
                    player_briefcase_value=player_briefcase.value,
                ),
                self._clock.now(),
            )
            return

        state.reject_offer()
        record.record_decision(round_number, Decision.REJECT)
        # Non-final round: move on to the next one. Final round leaves the game
        # in FINAL_SWAP_PENDING (endgame handled in a later phase).
        if state.status is GameStatus.IN_PROGRESS:
            state.advance_to_next_round()
