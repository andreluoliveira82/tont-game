"""Unit tests for the composition-root argument handling."""

from tont_game.__main__ import _parse_seed, _run_history, _select_command


def test_no_args_means_random_game() -> None:
    assert _parse_seed([]) is None


def test_integer_argument_is_used_as_seed() -> None:
    assert _parse_seed(["42"]) == 42


def test_non_integer_argument_is_ignored() -> None:
    assert _parse_seed(["abc"]) is None


def test_history_argument_selects_the_history_command() -> None:
    assert _select_command(["history"]) == "history"


def test_no_args_selects_the_play_command() -> None:
    assert _select_command([]) == "play"


def test_seed_argument_selects_the_play_command() -> None:
    assert _select_command(["42"]) == "play"


class _RecordingConsole:
    def __init__(self) -> None:
        self.outputs: list[str] = []

    def write(self, text: str) -> None:
        self.outputs.append(text)

    def read_line(self, prompt: str) -> str:  # pragma: no cover - unused here
        raise AssertionError("history commands do not read input")


class _EmptyRepository:
    def save(self, record: object) -> None:  # pragma: no cover - unused here
        raise NotImplementedError

    def list_summaries(self) -> list:
        return []

    def get(self, game_id: object) -> None:
        return None


def _history(args: list[str]) -> str:
    console = _RecordingConsole()
    _run_history(args, console, _EmptyRepository())  # type: ignore[arg-type]
    return "\n".join(console.outputs)


def test_history_without_subcommand_lists() -> None:
    assert "histórico" in _history(["history"])


def test_history_show_without_id_shows_usage() -> None:
    assert "Uso:" in _history(["history", "show"])


def test_history_show_routes_to_show() -> None:
    assert "inválido" in _history(["history", "show", "not-a-uuid"])


def test_history_unknown_subcommand_is_reported() -> None:
    assert "desconhecido" in _history(["history", "bogus"])
