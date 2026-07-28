"""GameRecord: append-only factual history of a game.

The record is the authority over what actually happened; it does not validate
game rules (that is the domain's job) and never references the mutable
GameState. Singular facts (player briefcase, offer/decision per round, official
result) are write-once. Accessors return immutable views.
"""

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from tont_game.domain.errors import HistoryError, OfficialResultAlreadySetError
from tont_game.domain.history.records import (
    BankerOfferRecord,
    BriefcaseOpeningRecord,
    Decision,
    OfficialResult,
)
from tont_game.domain.history.round_record import RoundRecord
from tont_game.domain.value_objects.money import Money


class GameRecord:
    def __init__(
        self,
        game_id: UUID,
        started_at: datetime,
        initial_distribution: Iterable[tuple[int, Money]],
        seed: int | None = None,
    ) -> None:
        self._game_id = game_id
        self._started_at = started_at
        self._initial_distribution: tuple[tuple[int, Money], ...] = tuple(
            initial_distribution
        )
        self._seed = seed
        self._player_briefcase_number: int | None = None
        self._rounds: list[RoundRecord] = []
        self._official_result: OfficialResult | None = None
        self._finished_at: datetime | None = None

    # --- read-only properties ------------------------------------------------

    @property
    def game_id(self) -> UUID:
        return self._game_id

    @property
    def started_at(self) -> datetime:
        return self._started_at

    @property
    def finished_at(self) -> datetime | None:
        return self._finished_at

    @property
    def seed(self) -> int | None:
        return self._seed

    @property
    def initial_distribution(self) -> tuple[tuple[int, Money], ...]:
        return self._initial_distribution

    @property
    def player_briefcase_number(self) -> int | None:
        return self._player_briefcase_number

    @property
    def rounds(self) -> tuple[RoundRecord, ...]:
        return tuple(self._rounds)

    @property
    def official_result(self) -> OfficialResult | None:
        return self._official_result

    # --- append-only recording ----------------------------------------------

    def record_player_briefcase(self, number: int) -> None:
        if self._player_briefcase_number is not None:
            raise HistoryError("The player briefcase has already been recorded.")
        self._player_briefcase_number = number

    def record_opening(
        self, round_number: int, briefcase_number: int, value: Money
    ) -> None:
        index = self._round_index(round_number)
        self._rounds[index] = self._rounds[index].with_opening(
            BriefcaseOpeningRecord(briefcase_number=briefcase_number, value=value)
        )

    def record_offer(
        self,
        round_number: int,
        offer: Money,
        percentage: Decimal,
        remaining_values: Iterable[Money],
    ) -> None:
        index = self._round_index(round_number)
        self._rounds[index] = self._rounds[index].with_offer(
            BankerOfferRecord(
                round_number=round_number,
                offer=offer,
                percentage=percentage,
                remaining_values=tuple(remaining_values),
            )
        )

    def record_decision(self, round_number: int, decision: Decision) -> None:
        index = self._round_index(round_number)
        self._rounds[index] = self._rounds[index].with_decision(decision)

    def close(self, official_result: OfficialResult, finished_at: datetime) -> None:
        if self._official_result is not None:
            raise OfficialResultAlreadySetError(
                "The official result has already been set."
            )
        self._official_result = official_result
        self._finished_at = finished_at

    # --- helpers -------------------------------------------------------------

    def _round_index(self, round_number: int) -> int:
        for index, record in enumerate(self._rounds):
            if record.round_number == round_number:
                return index
        self._rounds.append(RoundRecord(round_number))
        return len(self._rounds) - 1
