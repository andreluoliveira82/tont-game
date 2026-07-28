"""GameState: the aggregate root that represents the current state of a game.

Scope (Phase 2): it models the initial game, the 9-round structure and the
structural invariants around selecting the player's briefcase and opening
briefcases round by round. It does NOT know about banker offers, player
decisions, the endgame swap, the official result, randomness, the game
record or the post-game simulation — those belong to later phases.

Distribution of values to briefcases is provided from the outside (an ordered
sequence of values). The shuffling that produces that order is Phase 3.
"""

from collections.abc import Iterable

from tont_game.domain.entities.briefcase import Briefcase
from tont_game.domain.errors import (
    BriefcaseAlreadyOpenedError,
    GameConfigurationError,
    InvalidBriefcaseNumberError,
    InvalidGameStateError,
    NoMoreRoundsError,
    NoPendingOfferError,
    PlayerBriefcaseProtectedError,
    RoundLimitExceededError,
    RoundNotCompleteError,
)
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money
from tont_game.domain.value_objects.round_schedule import RoundSchedule

TOTAL_BRIEFCASES = 26
CLOSED_AT_ENDGAME = 2


class GameState:
    """Aggregate root holding briefcases, round progress and lifecycle status."""

    def __init__(
        self, briefcases: Iterable[Briefcase], schedule: RoundSchedule
    ) -> None:
        cases = list(briefcases)
        _validate_configuration(cases, schedule)
        self._briefcases: dict[int, Briefcase] = {case.number: case for case in cases}
        self._schedule = schedule
        self._player_number: int | None = None
        self._status = GameStatus.NOT_STARTED
        self._current_round = 1
        self._openings_in_current_round = 0
        self._current_offer: Money | None = None
        self._final_swap_applied = False

    @classmethod
    def create(
        cls,
        values: Iterable[Money],
        schedule: RoundSchedule | None = None,
    ) -> "GameState":
        """Build an initial game from an ordered sequence of values.

        Briefcases are numbered ``1..N`` following the order of ``values``.
        """
        schedule = schedule or RoundSchedule()
        briefcases = [
            Briefcase(number=index, value=value)
            for index, value in enumerate(values, start=1)
        ]
        return cls(briefcases, schedule)

    # --- lifecycle -----------------------------------------------------------

    @property
    def status(self) -> GameStatus:
        return self._status

    def select_player_briefcase(self, number: int) -> None:
        """Choose the protected player briefcase and start the game."""
        if self._status is not GameStatus.NOT_STARTED:
            raise InvalidGameStateError(
                "The player briefcase can only be selected before the game starts."
            )
        self._require_briefcase(number)
        self._player_number = number
        self._status = GameStatus.IN_PROGRESS

    # --- rounds --------------------------------------------------------------

    @property
    def current_round(self) -> int:
        return self._current_round

    def openings_required_in_current_round(self) -> int:
        return self._schedule.openings_for_round(self._current_round)

    def openings_remaining_in_current_round(self) -> int:
        return (
            self.openings_required_in_current_round() - self._openings_in_current_round
        )

    def is_current_round_complete(self) -> bool:
        return self.openings_remaining_in_current_round() == 0

    def has_next_round(self) -> bool:
        return self._current_round < self._schedule.total_rounds

    def all_rounds_completed(self) -> bool:
        return not self.has_next_round() and self.is_current_round_complete()

    def open_briefcase(self, number: int) -> Briefcase:
        """Open an available briefcase for the current round."""
        self._ensure_status(GameStatus.IN_PROGRESS)
        briefcase = self._require_briefcase(number)
        if number == self._player_number:
            raise PlayerBriefcaseProtectedError(
                "The player's briefcase cannot be opened during normal rounds."
            )
        if briefcase.opened:
            raise BriefcaseAlreadyOpenedError(f"Briefcase {number} is already opened.")
        if self.is_current_round_complete():
            raise RoundLimitExceededError(
                f"Round {self._current_round} has no remaining openings."
            )
        briefcase.open()
        self._openings_in_current_round += 1
        return briefcase

    def advance_to_next_round(self) -> None:
        """Move to the next round once the current one is complete."""
        self._ensure_status(GameStatus.IN_PROGRESS)
        if not self.is_current_round_complete():
            raise RoundNotCompleteError(
                f"Round {self._current_round} is not complete yet."
            )
        if not self.has_next_round():
            raise NoMoreRoundsError("There are no more rounds to advance to.")
        self._current_round += 1
        self._openings_in_current_round = 0

    # --- offer and decision --------------------------------------------------

    @property
    def current_offer(self) -> Money | None:
        return self._current_offer

    def is_over(self) -> bool:
        return self._status in (GameStatus.ACCEPTED, GameStatus.FINISHED)

    def set_pending_offer(self, offer: Money) -> None:
        """Register the banker's offer for the (completed) current round."""
        self._ensure_status(GameStatus.IN_PROGRESS)
        if not self.is_current_round_complete():
            raise InvalidGameStateError(
                "An offer can only be made once the current round is complete."
            )
        self._current_offer = offer
        self._status = GameStatus.OFFER_PENDING

    def accept_offer(self) -> Money:
        """Accept the pending offer, ending the game. Cannot be done twice."""
        if self._status is not GameStatus.OFFER_PENDING or self._current_offer is None:
            raise NoPendingOfferError("There is no pending offer to accept.")
        self._status = GameStatus.ACCEPTED
        return self._current_offer

    def reject_offer(self) -> None:
        """Reject the pending offer.

        On a non-final round the game returns to ``IN_PROGRESS`` (ready to
        advance); on the final round it moves to ``FINAL_SWAP_PENDING`` (the
        endgame, handled in a later phase).
        """
        if self._status is not GameStatus.OFFER_PENDING or self._current_offer is None:
            raise NoPendingOfferError("There is no pending offer to reject.")
        self._current_offer = None
        if self.has_next_round():
            self._status = GameStatus.IN_PROGRESS
        else:
            self._status = GameStatus.FINAL_SWAP_PENDING

    # --- endgame -------------------------------------------------------------

    def apply_final_swap(self) -> None:
        """Swap the player's briefcase for the single remaining closed one.

        Only valid in ``FINAL_SWAP_PENDING`` and at most once.
        """
        self._ensure_status(GameStatus.FINAL_SWAP_PENDING)
        if self._final_swap_applied:
            raise InvalidGameStateError("The final swap has already been applied.")
        others = self.available_briefcases()
        if len(others) != 1:
            raise InvalidGameStateError(
                "The final swap requires exactly one other closed briefcase."
            )
        self._player_number = others[0].number
        self._final_swap_applied = True

    def reveal_final_and_finish(self) -> Money:
        """Reveal the two last briefcases and finish the game.

        Only valid in ``FINAL_SWAP_PENDING``. Returns the value of the player's
        final briefcase. Transitions directly to ``FINISHED``.
        """
        self._ensure_status(GameStatus.FINAL_SWAP_PENDING)
        for briefcase in self.closed_briefcases():
            briefcase.open()
        self._status = GameStatus.FINISHED
        final_briefcase = self.player_briefcase
        assert final_briefcase is not None  # player is always set at endgame
        return final_briefcase.value

    # --- queries -------------------------------------------------------------

    @property
    def player_briefcase(self) -> Briefcase | None:
        if self._player_number is None:
            return None
        return self._briefcases[self._player_number]

    def briefcase(self, number: int) -> Briefcase:
        return self._require_briefcase(number)

    def all_briefcases(self) -> tuple[Briefcase, ...]:
        return tuple(self._briefcases[n] for n in sorted(self._briefcases))

    def opened_briefcases(self) -> tuple[Briefcase, ...]:
        return tuple(case for case in self.all_briefcases() if case.opened)

    def closed_briefcases(self) -> tuple[Briefcase, ...]:
        return tuple(case for case in self.all_briefcases() if not case.opened)

    def available_briefcases(self) -> tuple[Briefcase, ...]:
        """Closed briefcases that may be opened (excludes the player's)."""
        return tuple(
            case
            for case in self.closed_briefcases()
            if case.number != self._player_number
        )

    def remaining_values(self) -> tuple[Money, ...]:
        """Values not yet revealed (includes the player's briefcase value)."""
        return tuple(case.value for case in self.closed_briefcases())

    def closed_briefcase_count(self) -> int:
        return len(self.closed_briefcases())

    # --- helpers -------------------------------------------------------------

    def _require_briefcase(self, number: int) -> Briefcase:
        try:
            return self._briefcases[number]
        except KeyError:
            raise InvalidBriefcaseNumberError(
                f"Briefcase {number} does not exist."
            ) from None

    def _ensure_status(self, expected: GameStatus) -> None:
        if self._status is not expected:
            raise InvalidGameStateError(
                f"Operation requires status {expected.value}, "
                f"but current status is {self._status.value}."
            )


def _validate_configuration(
    briefcases: list[Briefcase], schedule: RoundSchedule
) -> None:
    if len(briefcases) != TOTAL_BRIEFCASES:
        raise GameConfigurationError(
            f"A game must have exactly {TOTAL_BRIEFCASES} briefcases, "
            f"got {len(briefcases)}."
        )
    numbers = sorted(case.number for case in briefcases)
    if numbers != list(range(1, TOTAL_BRIEFCASES + 1)):
        raise GameConfigurationError(
            f"Briefcases must be numbered 1..{TOTAL_BRIEFCASES} without gaps "
            "or duplicates."
        )
    if schedule.total_openings + CLOSED_AT_ENDGAME != TOTAL_BRIEFCASES:
        raise GameConfigurationError(
            "The round schedule must leave exactly "
            f"{CLOSED_AT_ENDGAME} closed briefcases at the endgame "
            f"(schedule opens {schedule.total_openings})."
        )
