"""Merged-cell handling — SheetModel.merged_cells must be respected."""

from __future__ import annotations

from whitebox.renderer import render_workbook
from whitebox.sheets.base import Cell, CellStyle, ColumnSpec, Row, SheetModel


def test_merged_cells_applied() -> None:
    model = SheetModel(
        sheet_name="M",
        columns=(
            ColumnSpec("a", "str"),
            ColumnSpec("b", "str"),
            ColumnSpec("c", "str"),
        ),
        rows=(
            Row(
                cells=(
                    Cell("x", CellStyle(classes=("str",))),
                    Cell(None, CellStyle(classes=("str",))),
                    Cell(None, CellStyle(classes=("str",))),
                )
            ),
        ),
        merged_cells=("A2:C2",),
    )
    wb = render_workbook([model])
    ws = wb["M"]
    assert "A2:C2" in [str(r) for r in ws.merged_cells.ranges]


def test_no_merge_by_default() -> None:
    model = SheetModel(
        sheet_name="M",
        columns=(ColumnSpec("a", "str"),),
    )
    wb = render_workbook([model])
    assert list(wb["M"].merged_cells.ranges) == []
