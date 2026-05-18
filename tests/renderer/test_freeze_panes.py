"""Freeze-pane handling."""

from __future__ import annotations

import pytest

from whitebox.renderer import render_workbook
from whitebox.sheets.base import ColumnSpec, SheetModel


@pytest.mark.parametrize("freeze", ["A2", "B2", "D2", "E2"])
def test_freeze_pane_value_preserved(freeze: str) -> None:
    model = SheetModel(
        sheet_name="F",
        columns=(ColumnSpec("a", "str"), ColumnSpec("b", "str")),
        freeze_panes=freeze,
    )
    wb = render_workbook([model])
    assert wb["F"].freeze_panes == freeze


def test_no_freeze_when_none() -> None:
    model = SheetModel(
        sheet_name="F",
        columns=(ColumnSpec("a", "str"),),
        freeze_panes=None,
    )
    wb = render_workbook([model])
    # openpyxl reports None when no freeze is set.
    assert wb["F"].freeze_panes in (None, "")
