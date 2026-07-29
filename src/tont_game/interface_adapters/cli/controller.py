"""CLI controller: drives a full game through the existing use cases.

It contains no business rules: it reads input, delegates every action to a use
case, catches domain errors to re-prompt, and formats output via the presenters.
"""

from tont_game.application.game_session import GameSession
from tont_game.application.use_cases.decide_final_swap import DecideFinalSwap
from tont_game.application.use_cases.decide_offer import DecideOffer
from tont_game.application.use_cases.open_briefcase import OpenBriefcase
from tont_game.application.use_cases.process_banker_offer import ProcessBankerOffer
from tont_game.application.use_cases.run_post_game_simulation import (
    RunPostGameSimulation,
)
from tont_game.application.use_cases.select_initial_briefcase import (
    SelectInitialBriefcase,
)
from tont_game.application.use_cases.start_game import StartGame
from tont_game.domain.clock import Clock
from tont_game.domain.errors import DomainError
from tont_game.domain.history.records import Decision, EndingType
from tont_game.domain.identifiers import GameIdGenerator
from tont_game.domain.randomness import RandomSource
from tont_game.domain.services.banker import BankerStrategy
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money
from tont_game.interface_adapters.cli import narration, presenters
from tont_game.interface_adapters.cli.views import Console

_ACCEPT_INPUTS = frozenset({"t", "topa", "s", "sim"})
_REJECT_INPUTS = frozenset({"n", "nao", "não"})
_YES_INPUTS = frozenset({"s", "sim"})
_NO_INPUTS = frozenset({"n", "nao", "não"})

# Show the full list of remaining values only when few remain (endgame tension);
# otherwise the compact status line (with the value span) is enough.
_FEW_VALUES = 6


class CliController:
    def __init__(
        self,
        console: Console,
        clock: Clock,
        id_generator: GameIdGenerator,
        random_source: RandomSource,
        banker_strategy: BankerStrategy,
        seed: int | None = None,
    ) -> None:
        self._console = console
        self._clock = clock
        self._id_generator = id_generator
        self._random_source = random_source
        self._strategy = banker_strategy
        self._seed = seed

    def run(self) -> None:
        try:
            self._play()
        except (EOFError, KeyboardInterrupt):
            self._console.write(presenters.aborted())

    # --- flow ----------------------------------------------------------------

    def _play(self) -> None:
        session = StartGame(self._clock, self._id_generator).execute(
            self._random_source, seed=self._seed
        )
        self._console.write(presenters.welcome())
        if self._seed is not None:
            self._console.write(presenters.seed_notice(self._seed))
        self._select_initial_briefcase(session)

        state = session.game_state
        while not state.is_over() and state.status is not GameStatus.FINAL_SWAP_PENDING:
            self._play_round(session)

        if state.status is GameStatus.FINAL_SWAP_PENDING:
            self._resolve_endgame(session)
        else:
            self._present_topa_result(session)

        self._maybe_simulate(session)

    def _select_initial_briefcase(self, session: GameSession) -> None:
        while True:
            number = self._read_int("Escolha a sua maleta inicial (1 a 26): ")
            if number is None:
                continue
            try:
                SelectInitialBriefcase().execute(session, number)
                self._console.write(presenters.player_briefcase(number))
                return
            except DomainError as error:
                self._console.write(presenters.error_message(error))

    def _play_round(self, session: GameSession) -> None:
        state = session.game_state
        self._console.write(presenters.round_header(state.current_round))
        self._write_status(session)
        self._write_available(session)
        remaining = state.remaining_values()
        if len(remaining) <= _FEW_VALUES:
            self._console.write(presenters.remaining_values(remaining))

        while not state.is_current_round_complete():
            left = state.openings_remaining_in_current_round()
            number = self._read_int(f"Abrir maleta ({left} nesta rodada) — número: ")
            if number is None:
                continue
            try:
                briefcase = OpenBriefcase().execute(session, number)
                self._console.write(presenters.opened_briefcase(briefcase))
            except DomainError as error:
                self._console.write(presenters.error_message(error))
                self._write_available(session)

        offer = ProcessBankerOffer(self._strategy).execute(session)
        player = state.player_briefcase
        assert player is not None
        self._console.write(
            presenters.decision_block(
                offer_value=offer,
                round_number=state.current_round,
                remaining=state.remaining_values(),
                player_number=player.number,
                closed_count=state.closed_briefcase_count(),
            )
        )
        decision = self._prompt_decision()
        DecideOffer(self._clock).execute(session, decision)

    def _resolve_endgame(self, session: GameSession) -> None:
        state = session.game_state
        self._console.write(presenters.endgame_intro())

        # Capture both briefcases BEFORE the swap, so the reveal keeps the right
        # identities regardless of the decision.
        player = state.player_briefcase
        assert player is not None
        other = state.available_briefcases()[0]
        original_number, original_value = player.number, player.value
        other_number, other_value = other.number, other.value

        swap = self._prompt_yes_no(
            "Deseja trocar a sua maleta pela última maleta fechada? "
            "(s/sim = sim · n/nao/não = não): "
        )
        DecideFinalSwap(self._clock).execute(session, swap)
        self._console.write(
            presenters.endgame_reveal(
                original_number, original_value, other_number, other_value, swap
            )
        )

    def _present_topa_result(self, session: GameSession) -> None:
        result = session.game_record.official_result
        assert result is not None
        self._console.write(presenters.official_result(result))
        self._narrate_ending(
            result.amount_received, result.player_briefcase_value, session
        )

    def _narrate_ending(self, got: Money, gave_up: Money, session: GameSession) -> None:
        values = [value for _, value in session.game_record.initial_distribution]
        moment = narration.moment_for(got, gave_up, max(values), min(values))
        if moment is None:
            return
        variants = narration.messages(moment)
        self._console.write(self._random_source.shuffle(variants)[0])

    def _maybe_simulate(self, session: GameSession) -> None:
        result = session.game_record.official_result
        assert result is not None
        if result.ending_type is not EndingType.OFFER_ACCEPTED:
            return
        if self._prompt_yes_no(
            "Deseja simular o que teria acontecido se continuasse? "
            "(s/sim · n/nao/não): "
        ):
            simulation = RunPostGameSimulation().execute(session.game_record)
            self._console.write(presenters.simulation_comparison(simulation))

    # --- presentation helpers ------------------------------------------------

    def _write_status(self, session: GameSession) -> None:
        state = session.game_state
        player = state.player_briefcase
        assert player is not None
        self._console.write(
            presenters.status_line(
                round_number=state.current_round,
                player_number=player.number,
                closed_count=state.closed_briefcase_count(),
                remaining=state.remaining_values(),
            )
        )

    def _write_available(self, session: GameSession) -> None:
        numbers = [
            briefcase.number for briefcase in session.game_state.available_briefcases()
        ]
        self._console.write(presenters.available_briefcases(numbers))

    # --- input helpers -------------------------------------------------------

    def _read_int(self, prompt: str) -> int | None:
        raw = self._console.read_line(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            self._console.write("Entrada inválida. Digite um número.")
            return None

    def _prompt_decision(self) -> Decision:
        while True:
            answer = (
                self._console.read_line(
                    "Topa ou Não Topa? (t/topa/s/sim = Topa · n/nao/não = Não Topa): "
                )
                .strip()
                .lower()
            )
            if answer in _ACCEPT_INPUTS:
                return Decision.ACCEPT
            if answer in _REJECT_INPUTS:
                return Decision.REJECT
            self._console.write("Resposta inválida. Digite Topa (t) ou Não Topa (n).")

    def _prompt_yes_no(self, prompt: str) -> bool:
        while True:
            answer = self._console.read_line(prompt).strip().lower()
            if answer in _YES_INPUTS:
                return True
            if answer in _NO_INPUTS:
                return False
            self._console.write("Resposta inválida. Digite s (sim) ou n (não).")
