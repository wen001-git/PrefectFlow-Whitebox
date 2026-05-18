"""Common types for the pure ``whitebox.sheets`` layer.

Style intent is expressed as a small vocabulary of **semantic style class
names** — *not* as ``openpyxl`` style objects. The renderer (P2.3) owns
the mapping from these class names to fills, fonts, borders, and number
formats.

The vocabulary (frozen for P2.2; extend by ADR only) — see
``docs/mrc/1.3-sheets.en.md`` § 4 for visual semantics:

- ``"header"`` — default header row (blue background, bold, centered)
- ``"header-diff"`` — header cell of a highlight column (pink fill,
  orange font); applied automatically when a column is declared with
  ``highlight=True``
- ``"money"`` — currency cell (``$#,##0`` or ``$#,##0.00``)
- ``"money-int"`` — integer-valued currency cell (``$#,##0``)
- ``"percent"`` — percentage cell (``0.00%``)
- ``"float"`` — plain numeric (no number_format)
- ``"int"`` — integer (no thousands separator)
- ``"date"`` — date cell (Excel default serialization)
- ``"str"`` — plain text
- ``"diff"`` — body cell that fails the highlight predicate (``abs(value)
  > 0``); rendered with pink fill + orange font
- ``"total"`` — totals/summary row cell
- ``"warning-red"`` / ``"warning-grey"`` — reserved for future grouped
  highlights (unused by MRC)

These names align with the legacy style block at
``util/gen_remit_validation_report.py:19-86`` (referenced from
``docs/mrc/1.3-sheets.en.md`` § 4.2 / § 4.3).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

from pandas import DataFrame

# Allowed data_type values per docs/mrc/1.3-sheets.en.md § 4.1.
DataType = Literal["str", "money", "float", "int", "date", "percentage"]


@dataclass(frozen=True)
class CellStyle:
    """Semantic style descriptor for a single cell.

    ``classes`` is the *ordered* tuple of semantic class names (see module
    docstring vocabulary). Order matters only for renderer overlay
    semantics — later classes override earlier ones. The renderer is the
    sole authority on how each class maps to openpyxl primitives.
    """

    classes: tuple[str, ...] = ()
    number_format: str | None = None  # semantic hint (e.g. "$#,##0.00")

    def with_extra(self, *extra: str) -> CellStyle:
        """Return a new CellStyle with additional class names appended."""
        return CellStyle(
            classes=self.classes + tuple(extra),
            number_format=self.number_format,
        )


@dataclass(frozen=True)
class Cell:
    """A single rendered cell value plus its style intent.

    ``value`` is the *raw* Python value (already rounded / coerced to the
    sheet's contract). The renderer writes it via openpyxl's natural
    type-dispatch; semantic styling is applied on top via ``style``.
    """

    value: Any
    style: CellStyle = field(default_factory=CellStyle)


@dataclass(frozen=True)
class Row:
    """A row of cells aligned 1:1 with ``SheetModel.columns``.

    ``row_classes`` is reserved for row-level overlays such as group
    banding or "total" row styling. Empty for vanilla data rows.
    """

    cells: tuple[Cell, ...]
    row_classes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ColumnSpec:
    """One worksheet column definition.

    Mirrors the legacy ``_validation_report_col`` helper at
    ``util/gen_remit_validation_report.py:1157-1167`` (cited via
    ``docs/mrc/1.3-sheets.en.md`` § 4.1):

    - ``key`` — column name in the validator DataFrame (= XLSX header).
      ``original_column == column`` always for MRC (no renames).
    - ``data_type`` — drives the renderer's number_format choice
      (see vocabulary above).
    - ``round_to`` — if set, body values are rounded with ``round(v, n)``
      before being placed into a ``Cell``. ``None`` means "no rounding".
    - ``highlight`` — column is in the highlight list (header gets
      ``header-diff`` class; each body cell whose ``abs(value) > 0`` gets
      a ``diff`` class). Matches legacy ``threshold=0`` highlight rule
      (``docs/mrc/1.3-sheets.en.md`` § 4.3).
    - ``width`` — explicit column width (column index measured in Excel
      character units); ``None`` defers to auto-width / renderer default
      of 20 (legacy ``default_column_width = 20``).
    """

    key: str
    data_type: DataType = "str"
    round_to: int | None = None
    highlight: bool = False
    width: int | None = None
    header: str | None = None  # display label; defaults to ``key``

    @property
    def header_label(self) -> str:
        return self.header if self.header is not None else self.key


@dataclass(frozen=True)
class SheetSection:
    """An optional named grouping of consecutive rows.

    Not used by any MRC sheet (all 5 are flat tables), but the contract
    is part of the base API so non-MRC servicers can express grouped
    layouts (e.g. summary + detail bands) without a model change.
    """

    title: str
    rows: tuple[Row, ...]
    section_classes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SheetModel:
    """Fully-described worksheet content + style intent.

    The renderer consumes this and emits openpyxl bytes. The sheet model
    is intentionally pure data — no behavior, no IO, no openpyxl imports.

    Fields:
    - ``sheet_name`` — the worksheet tab name (matches XLSX tab).
    - ``columns`` — ordered tuple of ``ColumnSpec``; defines column order
      and per-column type/highlight contract.
    - ``rows`` — ordered tuple of body ``Row`` objects. ``len(row.cells)
      == len(columns)`` for every row.
    - ``header_style`` — style applied to the header row by default.
    - ``freeze_panes`` — openpyxl freeze_panes reference (e.g. ``"A2"``
      freezes row 1). ``None`` disables freeze.
    - ``merged_cells`` — tuple of A1-style ranges to merge (unused by
      MRC; present for future sheets).
    - ``column_widths`` — optional ``{column_key: width}`` overrides;
      complements ``ColumnSpec.width``.
    - ``sections`` — optional named row groupings; when present the
      renderer renders these *after* the flat ``rows`` table.
    - ``metadata`` — arbitrary string→string passthrough (e.g.
      ``"asofdate": "2026-04-30"``) for the renderer / UI to display.
    """

    sheet_name: str
    columns: tuple[ColumnSpec, ...]
    rows: tuple[Row, ...] = ()
    header_style: CellStyle = field(
        default_factory=lambda: CellStyle(classes=("header",))
    )
    freeze_panes: str | None = "A2"
    merged_cells: tuple[str, ...] = ()
    column_widths: Mapping[str, int] = field(default_factory=dict)
    sections: tuple[SheetSection, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def column_keys(self) -> tuple[str, ...]:
        return tuple(c.key for c in self.columns)

    def highlight_keys(self) -> tuple[str, ...]:
        return tuple(c.key for c in self.columns if c.highlight)


@dataclass(frozen=True)
class ValidatorOutput:
    """Minimal contract describing the input to a sheet builder.

    Validator implementations (P2.5+) are not yet pinned to a typed
    output class; for now we accept a ``pandas.DataFrame`` plus the
    discriminators every sheet builder needs:

    - ``servicer`` — string discriminator (matches
      ``whitebox.transform.models.ServicerId`` values).
    - ``df`` — the validator-produced DataFrame, already stamped with
      ``asofdate`` per the legacy convention (``mrc_validation.py``).
    - ``asofdate`` — optional explicit override; when ``None`` the
      builder reads ``df["asofdate"]`` (first row) or falls back to a
      blank cell.
    - ``validator_id`` — provenance string; carried through to
      ``SheetModel.metadata`` so the renderer / UI can show "produced
      by V3 mrc_check_general_info".

    Kept deliberately permissive — when P2.5 lands a typed
    ``ValidatorResult`` (B3 § 2.7), the builders can adopt the typed
    class without a model rewrite (the DataFrame stays the source of
    truth).
    """

    validator_id: str
    servicer: str
    df: DataFrame
    asofdate: date | None = None


__all__ = [
    "Cell",
    "CellStyle",
    "ColumnSpec",
    "DataType",
    "Row",
    "SheetModel",
    "SheetSection",
    "ValidatorOutput",
]
