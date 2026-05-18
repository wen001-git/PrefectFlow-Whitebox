"""Version-guard tests — pin enforcement is the renderer's only hard fail-fast."""

from __future__ import annotations

import pytest

from whitebox.renderer.version_guard import (
    PINNED_OPENPYXL_VERSION,
    RendererVersionError,
    ensure_openpyxl_pin,
)


def test_pinned_version_matches_constant() -> None:
    # Architecture freeze: 3.1.5 (docs/stage2/11.0-architecture.en.md § 2).
    assert PINNED_OPENPYXL_VERSION == "3.1.5"


def test_passes_when_versions_match() -> None:
    ensure_openpyxl_pin(actual_version="3.1.5")


@pytest.mark.parametrize(
    "bad_version",
    ["3.1.4", "3.1.6", "3.2.0", "4.0.0", "", "unknown"],
)
def test_raises_on_mismatch(bad_version: str) -> None:
    with pytest.raises(RendererVersionError) as exc:
        ensure_openpyxl_pin(actual_version=bad_version)
    msg = str(exc.value)
    assert "3.1.5" in msg
    # The bump-policy guidance must be discoverable from the error.
    assert "AGENTS.md" in msg
    assert "decisions.md" in msg


def test_runtime_openpyxl_matches_pin() -> None:
    """The .venv's installed openpyxl is the pinned version."""
    import openpyxl

    assert openpyxl.__version__ == PINNED_OPENPYXL_VERSION
