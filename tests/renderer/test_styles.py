"""Style registry tests — every semantic class resolves; snapshot matches golden."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from whitebox.renderer.styles import (
    OVERLAY_CLASSES,
    PRIMARY_CLASSES,
    STYLES,
    styles_snapshot,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "styles_snapshot.json"

# Vocabulary frozen in whitebox/sheets/base.py module docstring (P2.2).
SHEET_VOCAB: frozenset[str] = frozenset(
    {
        "header",
        "header-diff",
        "money",
        "money-int",
        "percent",
        "float",
        "int",
        "date",
        "str",
        "diff",
        "total",
        "warning-red",
        "warning-grey",
    }
)


def test_every_sheet_class_is_registered() -> None:
    """Every name the sheets layer may emit must have a renderer mapping."""
    missing = SHEET_VOCAB - STYLES.keys()
    assert not missing, f"sheet vocabulary not covered by renderer: {missing}"


def test_no_extra_unknown_classes() -> None:
    """The renderer must not silently expand the frozen vocabulary."""
    extra = STYLES.keys() - SHEET_VOCAB
    assert not extra, (
        f"renderer registers classes outside the frozen vocabulary: {extra}. "
        "Update whitebox/sheets/base.py docstring + an ADR before adding."
    )


def test_primary_overlay_partition_is_complete() -> None:
    assert set(PRIMARY_CLASSES).isdisjoint(OVERLAY_CLASSES)
    assert set(PRIMARY_CLASSES) | set(OVERLAY_CLASSES) == STYLES.keys()


@pytest.mark.parametrize("name", sorted(STYLES.keys()))
def test_named_style_is_constructable(name: str) -> None:
    spec = STYLES[name]
    if spec.role == "primary":
        ns = spec.to_named_style()
        assert ns.name == name
    else:
        with pytest.raises(ValueError):
            spec.to_named_style()


def test_snapshot_matches_golden_fixture() -> None:
    """If this fails: the golden file must be regenerated *intentionally* and
    a brief note added to the commit message (style-change ADR not required
    for additive changes; mandatory for any color / format mutation)."""
    expected = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    actual = styles_snapshot()
    assert actual == expected
