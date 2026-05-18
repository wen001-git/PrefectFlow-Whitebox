"""Stage 2 P2.2 — openpyxl renderer (the *only* runtime openpyxl client).

This subpackage owns the SheetModel → ``.xlsx`` bytes transformation
(``docs/stage2/11.0-architecture.en.md`` § 3). It maps the semantic
style-class vocabulary defined by :mod:`whitebox.sheets.base` onto
openpyxl primitives, applies the workbook-level conventions (freeze
panes, column widths, merged cells, header coloring, diff overlays),
and writes the result via openpyxl ``Workbook.save``.

Public surface
--------------

- :func:`render_workbook` — build a ``Workbook`` from a list of
  :class:`whitebox.sheets.base.SheetModel`.
- :func:`write_workbook` — persist a rendered workbook to disk.
- :data:`STYLES` — central semantic-class → :class:`StyleDefinition`
  registry (single source of truth; see :mod:`whitebox.renderer.styles`).
- :class:`RendererVersionError` — raised by :mod:`.version_guard` when
  openpyxl is not the pinned 3.1.5 release.

The version guard runs at import time so any mismatch fails fast,
before any sheet is rendered.
"""

from __future__ import annotations

from whitebox.renderer.styles import STYLES, StyleDefinition
from whitebox.renderer.version_guard import RendererVersionError, ensure_openpyxl_pin
from whitebox.renderer.workbook import render_workbook, write_workbook

# Fail fast on import: if the installed openpyxl is not the pinned
# 3.1.5 build the cell-identity contract is void; refuse to render.
ensure_openpyxl_pin()

__all__ = [
    "STYLES",
    "RendererVersionError",
    "StyleDefinition",
    "ensure_openpyxl_pin",
    "render_workbook",
    "write_workbook",
]
