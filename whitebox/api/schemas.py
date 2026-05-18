"""Pydantic response schemas for the whitebox.api FastAPI surface.

Stage 2 / P2.3 — **production contracts**. These shapes are what the
FE (``apps/web``) types itself against and what later engine / storage
todos must produce. ``Any`` is forbidden anywhere in this module;
``CellValue`` is the single narrow union of permitted scalar payloads.

Doc cross-references:

* ``docs/stage2/3.0-data-model.en.md`` § 2.7 (``ValidatorResult``),
  § 2.8 (``SheetPayload``), § 2.10 (``BaselineComparison``), § 4
  (Lineage Contract).
* ``docs/stage2/6.0-ui-architecture.en.md`` § 2.2 (entity hierarchy),
  § 3.2 (Cell drill-down panel), § 5 (8 features).
* ``docs/stage2/11.0-architecture.en.md`` § 4 (FastAPI layout).

Legacy XLSX column mapping is called out per-field with ``[legacy: …]``
markers; the column tuples live in :mod:`whitebox.transform.models`.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Narrow scalar union for cell payloads.
#
# Legacy XLSX cells are always one of: text, number, boolean, blank.
# We pick the smallest union that round-trips JSON cleanly *and* stays
# strict-typed (no ``Any``). ``None`` represents an empty / NULL cell.
# ---------------------------------------------------------------------------
CellValue: TypeAlias = str | int | float | bool | None


# ---------------------------------------------------------------------------
# Cross-cutting enums (kept as ``str`` Enums so JSON stays human-readable).
# ---------------------------------------------------------------------------


class RunStatus(str, Enum):
    """Lifecycle state of a validation run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DiffVerdict(str, Enum):
    """Verdict tier produced by ``tools/xlsx_diff.py``.

    Mirrors ``docs/stage2/11.0-architecture.en.md`` § 6.
    """

    PASS = "PASS"
    MINOR_DIFFS = "MINOR_DIFFS"
    MAJOR_DIFFS = "MAJOR_DIFFS"
    ERROR = "ERROR"


class DiffKind(str, Enum):
    """Categorical reason a cell was reported as different."""

    VALUE = "value"            # both sides present, payload differs
    MISSING_LEFT = "missing_left"
    MISSING_RIGHT = "missing_right"
    TYPE = "type"              # same string but different scalar type
    FORMAT = "format"          # value identical, number format differs


class LineageNodeKind(str, Enum):
    """Node taxonomy on the lineage graph.

    Aligned with ``docs/stage2/3.0-data-model.en.md`` § 4.1 (raw → CTE →
    validator → sheet cell chain). The FE renders different shapes /
    colours per kind.
    """

    SOURCE = "source"          # upstream raw table column
    TRANSFORM = "transform"    # CTE / pandas transform step
    VALIDATOR = "validator"    # registry-registered validator
    SHEET = "sheet"            # output sheet
    FIELD = "field"            # output column on a sheet (the leaf)


class LineageEdgeRelation(str, Enum):
    """Edge taxonomy on the lineage graph."""

    READS = "reads"            # transform/validator consumes a source
    WRITES = "writes"          # transform/validator produces a field
    DERIVES = "derives"        # field-to-field derivation


# ---------------------------------------------------------------------------
# Shared infrastructure schemas.
# ---------------------------------------------------------------------------


class _StrictModel(BaseModel):
    """Base model: forbid unknown fields so contract drift surfaces in tests."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(_StrictModel):
    status: Literal["ok"] = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.0.1"])


class Pagination(_StrictModel):
    """Standard pagination envelope used by every list endpoint."""

    total: int = Field(..., ge=0, description="Total matching rows across all pages.")
    limit: int = Field(..., ge=1, le=500)
    offset: int = Field(..., ge=0)


class ErrorDetail(_StrictModel):
    code: str = Field(..., examples=["NOT_IMPLEMENTED"])
    message: str
    hint: str | None = None


class ErrorResponse(_StrictModel):
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------


class RunSummary(_StrictModel):
    """One row in the ``GET /runs`` listing.

    [legacy: there is no XLSX column for run metadata — runs are new in
    Stage 2; ``servicer`` / ``remit_date`` map to the discriminators on
    ``MrcRemitFrame`` (data-model § 2.4).]
    """

    run_id: str = Field(..., examples=["run_2026_05_18_001"])
    servicer: str = Field(..., examples=["MRC"], description="Registry servicer id.")
    remit_date: date = Field(..., description="Logical remit cycle date for the run.")
    status: RunStatus
    created_at: datetime
    validators_passed: int = Field(..., ge=0)
    validators_failed: int = Field(..., ge=0)


class SheetSummary(_StrictModel):
    """Aggregated per-sheet stats shown on the run-detail page.

    [legacy: ``row_count`` matches the row count emitted by the
    per-sheet builder (``whitebox.sheets.<sheet>``); ``highlight_count``
    matches the count of ``ffc7ce``-shaded cells in the legacy XLSX
    (1.6-baseline.en.md § 3).]
    """

    sheet_name: str = Field(..., examples=["MRC_Advance_Check"])
    title: str = Field("", description="Human-readable tab title.")
    tab_order: int = Field(0, ge=0)
    row_count: int = Field(..., ge=0)
    column_count: int = Field(..., ge=0)
    highlight_count: int = Field(..., ge=0)


class RunDetail(RunSummary):
    """Full run record returned by ``GET /runs/{run_id}``.

    Extends :class:`RunSummary` with per-sheet stats and the diff
    verdict against the run's pinned baseline.
    """

    sheets: list[SheetSummary] = Field(default_factory=list)
    verdict: DiffVerdict
    baseline_run_id: str | None = Field(
        None,
        description="Baseline run id this run was compared against, if any.",
    )


class RunListResponse(_StrictModel):
    runs: list[RunSummary]
    pagination: Pagination


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------


class SheetColumn(_StrictModel):
    """Column descriptor for ``SheetData``.

    [legacy: ``id`` is the snake_case column name on the underlying
    pandas frame; ``label`` is the header text written into the XLSX.
    See ``whitebox.transform.models`` for the canonical column tuples.]
    """

    id: str = Field(..., examples=["diff_adv_bal"])
    label: str = Field(..., examples=["Δ Advance Balance"])
    dtype: Literal["string", "number", "integer", "boolean", "date"] = "string"
    is_highlight: bool = Field(
        False,
        description="True if this column participates in the highlight rule set.",
    )


class SheetCell(_StrictModel):
    """One sheet cell with optional provenance.

    [legacy: maps to a ``(row, col)`` coordinate in the openpyxl
    workbook; ``cell_ref`` uses A1 notation (``"C4"``).]
    """

    row: int = Field(..., ge=1, description="1-based row index, matching openpyxl.")
    column_id: str
    cell_ref: str = Field(..., examples=["C4"], description="A1 notation.")
    value: CellValue = None
    is_highlight: bool = False
    validator_id: str | None = Field(
        None,
        description="Validator that produced/inspected this cell, if any.",
    )


class SheetRow(_StrictModel):
    """One sheet row as a column-id → value mapping."""

    row_index: int = Field(..., ge=1)
    values: dict[str, CellValue]


class SheetData(_StrictModel):
    """Body of ``GET /runs/{run_id}/sheets/{sheet_name}``.

    [legacy: this is the JSON shape of one openpyxl worksheet — column
    list + rows + the subset of cells that carry highlighting.]
    """

    run_id: str
    sheet_name: str
    title: str = ""
    columns: list[SheetColumn]
    rows: list[SheetRow]
    highlighted_cells: list[SheetCell] = Field(default_factory=list)


class SheetListResponse(_StrictModel):
    run_id: str
    sheets: list[SheetSummary]


class CellProvenance(_StrictModel):
    """One step in the raw → transform → validator → cell chain.

    Cross-ref: ``3.0-data-model.en.md`` § 4.1.
    """

    kind: LineageNodeKind
    id: str
    label: str
    detail: str = ""


class CellDetail(_StrictModel):
    """Body of ``GET /runs/{run_id}/sheets/{sheet_name}/cells/{cell_ref}``.

    Powers the F1 cell drill-down panel
    (``6.0-ui-architecture.en.md`` § 3.2).
    """

    run_id: str
    sheet_name: str
    cell: SheetCell
    computed_expression: str | None = Field(
        None,
        description="Human-readable formula, e.g. ``adv_curr - adv_prev``.",
    )
    provenance: list[CellProvenance] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Diff (wraps tools/xlsx_diff.py output)
# ---------------------------------------------------------------------------


class DiffCell(_StrictModel):
    """One differing cell in an XLSX-vs-XLSX diff.

    [legacy: a row in the ``diffs`` array produced by
    ``tools/xlsx_diff.py``.]
    """

    sheet: str
    cell_ref: str = Field(..., examples=["C4"])
    column_id: str | None = None
    left: CellValue = None
    right: CellValue = None
    kind: DiffKind


class SheetDiff(_StrictModel):
    """Per-sheet bucket of differing cells."""

    sheet_name: str
    cells: list[DiffCell] = Field(default_factory=list)
    rows_added: int = Field(0, ge=0)
    rows_removed: int = Field(0, ge=0)
    cells_changed: int = Field(0, ge=0)


class DiffResponse(_StrictModel):
    """Body of ``GET /runs/{run_id}/diff``.

    Mirrors the JSON envelope of ``tools/xlsx_diff.py`` so the engine
    todo can wire one-to-one.
    """

    run_id: str
    compared_to: str = Field(..., description="The other run id this was diffed against.")
    verdict: DiffVerdict
    total_cells_changed: int = Field(..., ge=0)
    sheets: list[SheetDiff]


# ---------------------------------------------------------------------------
# Lineage (react-flow consumable)
# ---------------------------------------------------------------------------


class LineageNodeData(_StrictModel):
    """``data`` payload for a react-flow node."""

    label: str
    detail: str = ""


class LineagePosition(_StrictModel):
    """``position`` payload for a react-flow node."""

    x: float
    y: float


class LineageNode(_StrictModel):
    """react-flow-shaped node (``id`` / ``type`` / ``data`` / ``position``).

    The ``type`` field uses our domain taxonomy; the FE maps it to a
    custom react-flow node type for shape / colour rendering.
    """

    id: str
    type: LineageNodeKind
    data: LineageNodeData
    position: LineagePosition


class LineageEdge(_StrictModel):
    """react-flow-shaped edge.

    ``id`` / ``source`` / ``target`` are the three react-flow-required
    fields; ``relation`` is our domain taxonomy.
    """

    id: str
    source: str
    target: str
    relation: LineageEdgeRelation


class LineageGraph(_StrictModel):
    """Body of ``GET /lineage/fields/{field_id}``.

    Returns both *backward* (sources feeding this field) and *forward*
    (downstream consumers) lineage merged into a single graph.
    """

    field_id: str
    nodes: list[LineageNode]
    edges: list[LineageEdge]


class LineageField(_StrictModel):
    """One row in the lineage-known fields catalog."""

    field_id: str
    servicer: str
    sheet: str
    label: str = ""


class LineageFieldListResponse(_StrictModel):
    fields: list[LineageField]


# ---------------------------------------------------------------------------
# Export (501 placeholder until renderer wiring lands)
# ---------------------------------------------------------------------------


class ExportResponse(_StrictModel):
    """Body returned by ``GET /runs/{run_id}/export`` once wired.

    Until then ``GET /runs/{run_id}/export`` returns 501 +
    :class:`ErrorResponse`; this schema is declared so the OpenAPI
    surface advertises the eventual contract.
    """

    run_id: str
    format: Literal["xlsx"] = "xlsx"
    download_url: str
    byte_size: int = Field(..., ge=0)
    sha256: str


__all__ = [
    "CellDetail",
    "CellProvenance",
    "CellValue",
    "DiffCell",
    "DiffKind",
    "DiffResponse",
    "DiffVerdict",
    "ErrorDetail",
    "ErrorResponse",
    "ExportResponse",
    "HealthResponse",
    "LineageEdge",
    "LineageEdgeRelation",
    "LineageField",
    "LineageFieldListResponse",
    "LineageGraph",
    "LineageNode",
    "LineageNodeData",
    "LineageNodeKind",
    "LineagePosition",
    "Pagination",
    "RunDetail",
    "RunListResponse",
    "RunStatus",
    "RunSummary",
    "SheetCell",
    "SheetColumn",
    "SheetData",
    "SheetDiff",
    "SheetListResponse",
    "SheetRow",
    "SheetSummary",
]
