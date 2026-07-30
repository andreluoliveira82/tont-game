"""The web contract: turn a game session into plain, JSON-ready facts.

Pure functions, no I/O and no rules. Money is exposed as a decimal string;
the player's briefcase value stays hidden until the game is finished. The
front-end renders drama over these facts — it never computes game truth.
"""

from typing import Any

from tont_game.application.game_session import GameSession
from tont_game.domain.entities.game_state import GameState
from tont_game.domain.history.records import EndingType, OfficialResult
from tont_game.domain.simulation.post_game_simulation import SimulationResult
from tont_game.domain.value_objects.game_status import GameStatus
from tont_game.domain.value_objects.money import Money


def game_view(
    session: GameSession, simulation: SimulationResult | None = None
) -> dict[str, Any]:
    """Serialize the current game facts for the front-end."""
    state = session.game_state
    result = session.game_record.official_result
    return {
        "status": state.status.value,
        "current_round": state.current_round,
        "openings_remaining": state.openings_remaining_in_current_round(),
        "player_briefcase": _player_briefcase(state, result),
        "available_briefcases": [case.number for case in state.available_briefcases()],
        "opened_briefcases": [
            {"number": case.number, "value": _money(case.value)}
            for case in state.opened_briefcases()
        ],
        "remaining_values": [
            _money(value) for value in sorted(state.remaining_values())
        ],
        "current_offer": _money(state.current_offer) if state.current_offer else None,
        "official_result": _official_result(result),
        "simulation": _simulation(simulation),
        "available_actions": _available_actions(state, result, simulation),
    }


def _player_briefcase(
    state: GameState, result: OfficialResult | None
) -> dict[str, Any] | None:
    player = state.player_briefcase
    if player is None:
        return None
    revealed = result is not None
    return {
        "number": player.number,
        "value": _money(player.value) if revealed else None,
    }


def _official_result(result: OfficialResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "ending_type": result.ending_type.value,
        "amount_received": _money(result.amount_received),
        "player_briefcase_value": _money(result.player_briefcase_value),
        "swap_decision": result.swap_decision,
        "final_briefcase_number": result.final_briefcase_number,
        "final_briefcase_value": (
            _money(result.final_briefcase_value)
            if result.final_briefcase_value
            else None
        ),
    }


def _simulation(simulation: SimulationResult | None) -> dict[str, Any] | None:
    if simulation is None:
        return None
    return {
        "official": _money(simulation.official_amount),
        "hypothetical": _money(simulation.hypothetical_amount),
        "difference": _money(simulation.absolute_difference()),
        "hypothetical_is_higher": simulation.hypothetical_is_higher(),
    }


def _available_actions(
    state: GameState,
    result: OfficialResult | None,
    simulation: SimulationResult | None,
) -> list[str]:
    status = state.status
    if status is GameStatus.NOT_STARTED:
        return ["select_briefcase"]
    if status is GameStatus.IN_PROGRESS:
        return ["open_briefcase"]
    if status is GameStatus.OFFER_PENDING:
        return ["decide"]
    if status is GameStatus.FINAL_SWAP_PENDING:
        return ["decide_swap"]
    if result is not None and result.ending_type is EndingType.OFFER_ACCEPTED:
        return ["simulate"] if simulation is None else []
    return []


def _money(value: Money) -> str:
    return str(value.amount)
