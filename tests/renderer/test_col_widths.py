"""Column width handling — precedence: column_widths > ColumnSpec.width > default."""

from __future__ import annotations

from whitebox.renderer import render_workbook
from whitebox.renderer.formats import DEFAULT_COLUMN_WIDTH
from whitebox.sheets.base import ColumnSpec, SheetModel


def test_default_width_when_unspecified() -> None:
    model = SheetModel(
        sheet_name="W",
        columns=(ColumnSpec("a", "str"), ColumnSpec("b", "str")),
    )
    wb = render_workbook([model])
    ws = wb["W"]
    assert ws.column_dimensions["A"].width == DEFAULT_COLUMN_WIDTH
    assert ws.column_dimensions["B"].width == DEFAULT_COLUMN_WIDTH


def test_column_spec_width_takes_effect() -> None:
    model = SheetModel(
        sheet_name="W",
        columns=(
            ColumnSpec("a", "str", width=12),
            ColumnSpec("b", "str", width=25),
        ),
    )
    wb = render_workbook([model])
    ws = wb["W"]
    assert ws.column_dimensions["A"].width == 12
    assert ws.column_dimensions["B"].width == 25


def test_column_widths_override_beats_column_spec() -> None:
    model = SheetModel(
        sheet_name="W",
        columns=(
            ColumnSpec("a", "str", width=12),
            ColumnSpec("b", "str", width=25),
        ),
        column_widths={"a": 40},  # override only column A
    )
    wb = render_workbook([model])
    ws = wb["W"]
    assert ws.column_dimensions["A"].width == 40
    assert ws.column_dimensions["B"].width == 25  # ColumnSpec.width retained
