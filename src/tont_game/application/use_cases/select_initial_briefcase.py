"""SelectInitialBriefcase: choose the player's protected briefcase."""

from tont_game.application.game_session import GameSession


class SelectInitialBriefcase:
    def execute(self, session: GameSession, number: int) -> None:
        # Validate/execute in the domain first; only then record the fact.
        session.game_state.select_player_briefcase(number)
        session.game_record.record_player_briefcase(number)
