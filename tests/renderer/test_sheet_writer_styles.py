"""Per-cell style application tests — primary class + diff overlay."""

from __future__ import annotations

from whitebox.renderer import render_workbook
from whitebox.renderer.formats import (
    DIFF_FILL_COLOR,
    DIFF_FONT_COLOR,
    HEADER_FILL_COLOR,
    MONEY_FORMAT,
    MONEY_INT_FORMAT,
)
from whitebox.sheets.base import SheetModel


def _rgb_suffix(value: str | None) -> str | None:
    """openpyxl stores ``"00bccde9"`` for input ``"bccde9"``; compare loosely."""
    if value is None:
        return None
    return value[-6:].lower()


def test_money_cell_carries_money_number_format(
    minimal_models: list[SheetModel],
) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    # Row 2 col B = 100.55 (money)
    assert alpha.cell(row=2, column=2).number_format == MONEY_FORMAT


def test_money_int_cell_carries_money_int_format(
    minimal_models: list[SheetModel],
) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    # Row 2 col C = 0 (money-int)
    assert alpha.cell(row=2, column=3).number_format == MONEY_INT_FORMAT


def test_header_row_has_header_fill(minimal_models: list[SheetModel]) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    hdr = alpha.cell(row=1, column=1)
    assert _rgb_suffix(hdr.fill.start_color.rgb) == HEADER_FILL_COLOR.lower()
    assert hdr.font.bold is True


def test_header_diff_swaps_fill_and_font(minimal_models: list[SheetModel]) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    # column C ("diff") was declared highlight=True
    diff_hdr = alpha.cell(row=1, column=3)
    assert _rgb_suffix(diff_hdr.fill.start_color.rgb) == DIFF_FILL_COLOR.lower()
    assert _rgb_suffix(diff_hdr.font.color.rgb) == DIFF_FONT_COLOR.lower()
    assert diff_hdr.font.bold is True


def test_diff_overlay_paints_body_cell(minimal_models: list[SheetModel]) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    # Row 3 col C = 7.5 with classes ("money","diff")
    diff_cell = alpha.cell(row=3, column=3)
    assert _rgb_suffix(diff_cell.fill.start_color.rgb) == DIFF_FILL_COLOR.lower()
    assert _rgb_suffix(diff_cell.font.color.rgb) == DIFF_FONT_COLOR.lower()
    # Number format inherited from the primary "money" style.
    assert diff_cell.number_format == MONEY_FORMAT


def test_non_diff_body_cell_uses_default_font_color(
    minimal_models: list[SheetModel],
) -> None:
    wb = render_workbook(minimal_models)
    alpha = wb["Alpha"]
    cell_b2 = alpha.cell(row=2, column=2)  # 100.55 money — no diff
    assert _rgb_suffix(cell_b2.font.color.rgb) == "000000"
