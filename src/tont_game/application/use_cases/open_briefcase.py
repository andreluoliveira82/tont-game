"""OpenBriefcase: open an available briefcase in the current round."""

from tont_game.application.game_session import GameSession
from tont_game.domain.entities.briefcase import Briefcase


class OpenBriefcase:
    def execute(self, session: GameSession, number: int) -> Briefcase:
        # The domain validates and performs the opening; then it is recorded.
        briefcase = session.game_state.open_briefcase(number)
        session.game_record.record_opening(
            session.game_state.current_round, briefcase.number, briefcase.value
        )
        return briefcase
