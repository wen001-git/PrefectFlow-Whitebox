"""End-to-end check: all 5 MRC sheet builders are discoverable via the
shared sheet registry, with the chapter-1.0-mandated tab order.

Chapter ref: ``docs/mrc/1.0-toc.en.md`` § 4 (5-sheet XLSX order).
"""

from __future__ import annotations

import pytest

from whitebox.registry import sheet_registry
from whitebox.sheets import MRC_SHEET_IDS

EXPECTED_TAB_ORDER: tuple[tuple[str, int], ...] = (
    ("MRC_Summary_check", 1),
    ("MRC_General_Check", 2),
    ("MRC_Advance_Check", 3),
    ("MRC_ServiceFee_Check", 4),
    ("MRC_Adv_Info", 5),
)


def test_all_five_mrc_sheets_registered() -> None:
    ids = set(sheet_registry.ids())
    expected = {name for name, _ in EXPECTED_TAB_ORDER}
    assert expected.issubset(ids)
    assert set(MRC_SHEET_IDS) == expected


@pytest.mark.parametrize("sheet_id,tab_order", EXPECTED_TAB_ORDER)
def test_each_sheet_spec_has_chapter_metadata(sheet_id: str, tab_order: int) -> None:
    spec = sheet_registry.get(sheet_id)
    assert spec.servicer == "MRC"
    assert spec.tab_order == tab_order
    assert spec.title == sheet_id
    assert spec.column_count > 0


def test_sheet_ids_match_chapter_10_order() -> None:
    # Per 1.0-toc.en.md § 4, this is the authoritative XLSX tab order.
    assert tuple(name for name, _ in EXPECTED_TAB_ORDER) == MRC_SHEET_IDS
