"""Centralized number / date format strings and visual constants.

All format strings and palette colors used by the renderer live here so
the sheet writer and the style registry agree byte-for-byte. Values
mirror the legacy style block at ``util/gen_remit_validation_report.py``
lines 19-86 (cited via ``docs/mrc/1.3-sheets.en.md`` § 4.2 / § 4.3).
"""

from __future__ import annotations

MONEY_FORMAT = "$#,##0.00"
MONEY_INT_FORMAT = "$#,##0"
PERCENT_FORMAT = "0.00%"
NUMBER_FORMAT = "#,##0.00"
INT_FORMAT = "#,##0"

# Excel's "General" format — openpyxl's default for un-styled cells.
GENERAL_FORMAT = "General"

# Default column width (Excel character units), per 1.3 § 4.2 table
# (``default_column_width = 20``).
DEFAULT_COLUMN_WIDTH = 20

# Default font family used everywhere — ARIAL 12, black, regular.
DEFAULT_FONT_NAME = "ARIAL"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = "000000"

# Header fill (legacy ``header_style.fill.start_color`` — 1.3 § 4.3).
HEADER_FILL_COLOR = "bccde9"

# Highlight palette — used by both ``header-diff`` and the ``diff``
# body-cell overlay (legacy ``diff_column_style`` — 1.3 § 4.3).
DIFF_FILL_COLOR = "ffc7ce"
DIFF_FONT_COLOR = "df5006"

# Reserved future-use palette — kept here so any later expansion shares
# the same single source of truth.
DIFF_RELATION_FILL_COLOR = "a5a5a5"
DIFF_RELATION_FONT_COLOR = "ffffff"

__all__ = [
    "DEFAULT_COLUMN_WIDTH",
    "DEFAULT_FONT_COLOR",
    "DEFAULT_FONT_NAME",
    "DEFAULT_FONT_SIZE",
    "DIFF_FILL_COLOR",
    "DIFF_FONT_COLOR",
    "DIFF_RELATION_FILL_COLOR",
    "DIFF_RELATION_FONT_COLOR",
    "GENERAL_FORMAT",
    "HEADER_FILL_COLOR",
    "INT_FORMAT",
    "MONEY_FORMAT",
    "MONEY_INT_FORMAT",
    "NUMBER_FORMAT",
    "PERCENT_FORMAT",
]
