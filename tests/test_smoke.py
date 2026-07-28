"""Structural smoke test for the Phase 1 setup.

Verifies that the package is importable and exposes its version. It does not
test any game behavior — domain rules belong to later phases.
"""

import tont_game


def test_package_is_importable_and_exposes_version() -> None:
    assert isinstance(tont_game.__version__, str)
    assert tont_game.__version__
