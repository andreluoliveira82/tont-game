"""ProcessBankerOffer: compute the banker's offer and register it."""

from tont_game.application.game_session import GameSession
from tont_game.domain.services.banker import BankerStrategy
from tont_game.domain.value_objects.money import Money


class ProcessBankerOffer:
    def __init__(self, banker_strategy: BankerStrategy) -> None:
        self._strategy = banker_strategy

    def execute(self, session: GameSession) -> Money:
        state = session.game_state
        remaining_values = state.remaining_values()
        round_number = state.current_round
        offer = self._strategy.offer(remaining_values, round_number)
        percentage = self._strategy.percentage_for_round(round_number)
        # The domain gates the offer (round must be complete); then record it.
        state.set_pending_offer(offer)
        session.game_record.record_offer(
            round_number, offer, percentage, remaining_values
        )
        return offer
