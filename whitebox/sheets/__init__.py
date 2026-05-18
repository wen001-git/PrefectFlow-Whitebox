"""Stage 2 P2.2 — pure MRC sheet builders.

This subpackage owns the sheet-model construction step in the Stage 2
architecture (docs/stage2/11.0-architecture.en.md § 3): consume validator
outputs and transform outputs, produce a fully-described, openpyxl-free
``SheetModel`` per worksheet.

Strict purity contract:

- **No IO** — no file/network/db calls, no ``time.now()``, no env reads.
- **No openpyxl** — every style intent is a *semantic class name* (e.g.
  ``"header"``, ``"money"``, ``"diff"``). The downstream renderer module
  (P2.3 / ``d-renderer-pin``) maps these names to openpyxl ``NamedStyle``
  / fill / font objects.
- **No business logic** — the validator computes the diffs; this layer
  only *describes* how the resulting frame becomes a worksheet (column
  order, types, highlights, freeze panes, widths).
"""

from __future__ import annotations

from whitebox.sheets.base import (
    Cell,
    CellStyle,
    ColumnSpec,
    Row,
    SheetModel,
    SheetSection,
    ValidatorOutput,
)
from whitebox.sheets.mrc import MRC_SHEET_IDS, register_mrc_sheets

# Trigger sheet-spec registration at package import. Engine / renderer
# can rely on ``sheet_registry`` containing all 5 MRC sheets just by
# importing ``whitebox.sheets``.
register_mrc_sheets()

__all__ = [
    "MRC_SHEET_IDS",
    "Cell",
    "CellStyle",
    "ColumnSpec",
    "Row",
    "SheetModel",
    "SheetSection",
    "ValidatorOutput",
    "register_mrc_sheets",
]
