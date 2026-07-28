"""StartGame: create a shuffled game and initialize its history record."""

from collections.abc import Iterable

from tont_game.application.game_session import GameSession
from tont_game.domain.clock import Clock
from tont_game.domain.history.game_record import GameRecord
from tont_game.domain.identifiers import GameIdGenerator
from tont_game.domain.official_values import OFFICIAL_BRIEFCASE_VALUES
from tont_game.domain.randomness import RandomSource
from tont_game.domain.services.distribution import create_shuffled_game
from tont_game.domain.value_objects.money import Money
from tont_game.domain.value_objects.round_schedule import RoundSchedule


class StartGame:
    def __init__(self, clock: Clock, id_generator: GameIdGenerator) -> None:
        self._clock = clock
        self._id_generator = id_generator

    def execute(
        self,
        random_source: RandomSource,
        seed: int | None = None,
        values: Iterable[Money] = OFFICIAL_BRIEFCASE_VALUES,
        schedule: RoundSchedule | None = None,
    ) -> GameSession:
        game_state = create_shuffled_game(random_source, values, schedule)
        distribution = tuple(
            (briefcase.number, briefcase.value)
            for briefcase in game_state.all_briefcases()
        )
        game_record = GameRecord(
            game_id=self._id_generator.new_id(),
            started_at=self._clock.now(),
            initial_distribution=distribution,
            seed=seed,
        )
        return GameSession(game_state=game_state, game_record=game_record)
