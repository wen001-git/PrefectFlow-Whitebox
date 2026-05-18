"""Shared helpers for MRC sheet builders.

All functions are pure and openpyxl-free. The semantic style vocabulary
is defined in :mod:`whitebox.sheets.base`.

Highlight semantics (legacy rule — preserved verbatim):

- ``threshold = 0`` for every MRC highlight column.
- Comparison is strict ``abs(value) > 0`` after ``pd.to_numeric(errors=
  "coerce")``.
- ``NaN`` / non-numeric / exact ``0`` ⇒ no highlight.
- Source: ``util/gen_remit_validation_report.py:1764-1798`` (cited via
  ``docs/mrc/1.3-sheets.en.md`` § 4.3).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from typing import Any

import pandas as pd
from pandas import DataFrame

from whitebox.sheets.base import (
    Cell,
    CellStyle,
    ColumnSpec,
    DataType,
    Row,
    ValidatorOutput,
)

# ---------------------------------------------------------------------------
# Number-format constants (mirror legacy style block,
# gen_remit_validation_report.py:19-86 — see 1.3-sheets.en.md § 4.2).
# ---------------------------------------------------------------------------

MONEY_FORMAT = "$#,##0.00"
MONEY_INT_FORMAT = "$#,##0"
PERCENT_FORMAT = "0.00%"

# Default semantic style per data_type. Renderer can extend; helpers only
# emit semantic classes here.
_BASE_STYLE_BY_TYPE: dict[DataType, CellStyle] = {
    "str": CellStyle(classes=("str",)),
    "int": CellStyle(classes=("int",)),
    "float": CellStyle(classes=("float",)),
    "date": CellStyle(classes=("date",)),
    "percentage": CellStyle(classes=("percent",), number_format=PERCENT_FORMAT),
    # money default uses 2dp; ``coerce_money_cell`` swaps to int format
    # when the value is integer-valued (matches legacy ``data_type_format``
    # behavior — 1.3-sheets.en.md § 4.2).
    "money": CellStyle(classes=("money",), number_format=MONEY_FORMAT),
}


def _is_missing(value: Any) -> bool:
    """``True`` for ``None``, ``NaN`` (float or pandas NA), ``pd.NaT``."""
    if value is None:
        return True
    # pandas treats NaT / NaN uniformly via ``pd.isna``; guard against
    # arrays (we only ever call on scalars).
    try:
        result = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(result, bool):
        return result
    return False


def round_value(value: Any, ndigits: int | None) -> Any:
    """Round numeric ``value`` to ``ndigits``; pass through otherwise.

    Mirrors legacy ``sheet_df_round`` (gen_remit_validation_report.py,
    cited in 1.3-sheets.en.md § 3): ``round_to == 0`` → int cast,
    positive ``ndigits`` → 2dp rounding, NaN preserved, non-numerics
    pass through unchanged.
    """
    if ndigits is None:
        return value
    if _is_missing(value):
        return value
    if isinstance(value, bool):  # bool is an int subclass; keep as-is
        return value
    if isinstance(value, int | float):
        f = float(value)
        if math.isinf(f) or math.isnan(f):
            return f
        if ndigits == 0:
            return int(f)
        return round(f, ndigits)
    return value


def is_highlight_value(value: Any) -> bool:
    """Return ``True`` when ``abs(numeric(value)) > 0`` (legacy rule).

    Non-numeric and NaN return ``False`` (matches
    ``pd.to_numeric(errors='coerce')`` cascade — 1.3-sheets.en.md § 4.3).
    """
    if _is_missing(value):
        return False
    try:
        numeric = pd.to_numeric(value, errors="coerce")
    except (TypeError, ValueError):
        return False
    if _is_missing(numeric):
        return False
    try:
        f = float(numeric)
    except (TypeError, ValueError):
        return False
    if math.isnan(f) or math.isinf(f):
        return math.isinf(f)  # inf is genuinely > 0
    return abs(f) > 0.0


def coerce_money_cell(value: Any, *, highlight: bool = False) -> Cell:
    """Build a money cell following legacy ``data_type_format`` rules.

    - Missing / NaN values are coerced to ``0`` (1.3-sheets.en.md § 4.2).
    - Integer-valued amounts get ``money-int`` style + ``$#,##0`` format.
    - Other amounts keep ``money`` style + ``$#,##0.00`` format.
    """
    if _is_missing(value):
        value = 0

    try:
        as_float = float(value)
    except (TypeError, ValueError):
        # non-numeric in a money column: emit as-is with money style,
        # mirroring legacy which would render it raw.
        style = _BASE_STYLE_BY_TYPE["money"]
        return Cell(value=value, style=style.with_extra("diff") if highlight else style)

    if math.isnan(as_float) or math.isinf(as_float):
        style = _BASE_STYLE_BY_TYPE["money"]
        return Cell(value=as_float, style=style.with_extra("diff") if highlight else style)

    if as_float == int(as_float):
        style = CellStyle(classes=("money-int",), number_format=MONEY_INT_FORMAT)
        cell_value: Any = int(as_float)
    else:
        style = _BASE_STYLE_BY_TYPE["money"]
        cell_value = as_float

    if highlight:
        style = style.with_extra("diff")
    return Cell(value=cell_value, style=style)


def build_cell(value: Any, spec: ColumnSpec, *, highlight: bool = False) -> Cell:
    """Build a single body ``Cell`` honoring the column's data_type."""
    rounded = round_value(value, spec.round_to)

    if spec.data_type == "money":
        return coerce_money_cell(rounded, highlight=highlight)

    base = _BASE_STYLE_BY_TYPE[spec.data_type]

    # Normalize date / datetime to ``date`` so renderer dispatch is
    # uniform (legacy pandas serialization handles both).
    if spec.data_type == "date" and isinstance(rounded, datetime):
        rounded = rounded.date()

    style = base.with_extra("diff") if highlight else base
    if _is_missing(rounded):
        return Cell(value=None, style=style)
    return Cell(value=rounded, style=style)


def build_header_row(columns: Iterable[ColumnSpec]) -> Row:
    """Header row — column with ``highlight=True`` gets ``header-diff``."""
    cells: list[Cell] = []
    for col in columns:
        classes: tuple[str, ...] = ("header-diff",) if col.highlight else ("header",)
        cells.append(Cell(value=col.header_label, style=CellStyle(classes=classes)))
    return Row(cells=tuple(cells), row_classes=("header",))


def build_data_rows(df: DataFrame, columns: tuple[ColumnSpec, ...]) -> tuple[Row, ...]:
    """Project ``df`` onto ``columns`` and emit one ``Row`` per df row.

    Columns missing from the DataFrame are filled with ``None`` (mirrors
    legacy ``sheet_df_round`` which inserts ``np.nan`` for absent
    helper-declared columns — 1.3-sheets.en.md § 3).
    """
    if df.empty:
        return ()

    keys = [c.key for c in columns]
    # Reindex preserves row order; missing columns become NaN.
    projected = df.reindex(columns=keys)

    rows: list[Row] = []
    # ``itertuples(index=False, name=None)`` returns plain tuples — fastest
    # & avoids attribute-name sanitization issues for columns whose names
    # collide with Python identifiers (none for MRC, but cheap insurance).
    for record in projected.itertuples(index=False, name=None):
        cells: list[Cell] = []
        for col, raw in zip(columns, record, strict=True):
            highlight = col.highlight and is_highlight_value(raw)
            cells.append(build_cell(raw, col, highlight=highlight))
        rows.append(Row(cells=tuple(cells)))
    return tuple(rows)


def asofdate_metadata(inputs: ValidatorOutput) -> Mapping[str, str]:
    """Stable metadata bag echoed onto ``SheetModel.metadata``."""
    out: dict[str, str] = {
        "validator_id": inputs.validator_id,
        "servicer": inputs.servicer,
    }
    asof = _resolve_asofdate(inputs)
    if asof is not None:
        out["asofdate"] = asof.isoformat()
    return out


def _resolve_asofdate(inputs: ValidatorOutput) -> date | None:
    """Use the explicit override, else the first row's ``asofdate``."""
    if inputs.asofdate is not None:
        return inputs.asofdate
    if "asofdate" not in inputs.df.columns or inputs.df.empty:
        return None
    raw = inputs.df["asofdate"].iloc[0]
    if _is_missing(raw):
        return None
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    try:
        ts = pd.Timestamp(raw)
    except (TypeError, ValueError):
        return None
    if pd.isna(ts):
        return None
    result: date = ts.date()
    return result


__all__ = [
    "MONEY_FORMAT",
    "MONEY_INT_FORMAT",
    "PERCENT_FORMAT",
    "asofdate_metadata",
    "build_cell",
    "build_data_rows",
    "build_header_row",
    "coerce_money_cell",
    "is_highlight_value",
    "round_value",
]
