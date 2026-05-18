"""Shared fixtures for renderer tests."""

from __future__ import annotations

from datetime import date

import pytest

from whitebox.sheets.base import (
    Cell,
    CellStyle,
    ColumnSpec,
    Row,
    SheetModel,
)


def _cell(value: object, *classes: str, number_format: str | None = None) -> Cell:
    return Cell(value=value, style=CellStyle(classes=classes, number_format=number_format))


@pytest.fixture
def minimal_sheet_alpha() -> SheetModel:
    return SheetModel(
        sheet_name="Alpha",
        columns=(
            ColumnSpec("name", "str", width=15),
            ColumnSpec("amount", "money", round_to=2),
            ColumnSpec("diff", "money", round_to=2, highlight=True),
            ColumnSpec("asof", "date"),
        ),
        rows=(
            Row(
                cells=(
                    _cell("alpha", "str"),
                    _cell(100.55, "money", number_format="$#,##0.00"),
                    _cell(0, "money-int", number_format="$#,##0"),
                    _cell(date(2026, 4, 30), "date"),
                )
            ),
            Row(
                cells=(
                    _cell("bravo", "str"),
                    _cell(200, "money-int", number_format="$#,##0"),
                    _cell(7.5, "money", "diff", number_format="$#,##0.00"),
                    _cell(date(2026, 4, 30), "date"),
                )
            ),
        ),
        freeze_panes="B2",
    )


@pytest.fixture
def minimal_sheet_beta() -> SheetModel:
    return SheetModel(
        sheet_name="Beta",
        columns=(
            ColumnSpec("k", "str"),
            ColumnSpec("v", "float", round_to=2),
        ),
        rows=(
            Row(
                cells=(
                    _cell("x", "str"),
                    _cell(1.5, "float"),
                )
            ),
        ),
        freeze_panes="A2",
    )


@pytest.fixture
def minimal_models(
    minimal_sheet_alpha: SheetModel, minimal_sheet_beta: SheetModel
) -> list[SheetModel]:
    return [minimal_sheet_alpha, minimal_sheet_beta]
