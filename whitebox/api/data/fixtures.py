"""Typed fixture provider for the FastAPI contract layer.

# FIXTURE: replaced by engine/storage in later todos

Each public function returns fully-typed pydantic models matching
:mod:`whitebox.api.schemas`. FE devs can build screens against these
shapes today; replacing the body with real engine output is a
one-import change.

The fixture data is intentionally:

* **Stable** — deterministic ids and values so the OpenAPI snapshot
  test and request/response examples don't churn.
* **Realistic** — values follow the MRC seed sheets
  (``docs/stage2/4.0-validator-registry.en.md`` § 5.3) so FE screens
  look plausible end-to-end.
* **Servicer-agnostic** — keyed by ``servicer`` everywhere; adding a
  second servicer here is a copy-paste, not a re-architecture.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from whitebox.api.schemas import (
    CellDetail,
    CellProvenance,
    DiffCell,
    DiffKind,
    DiffResponse,
    DiffVerdict,
    LineageEdge,
    LineageEdgeRelation,
    LineageField,
    LineageGraph,
    LineageNode,
    LineageNodeData,
    LineageNodeKind,
    LineagePosition,
    RunDetail,
    RunStatus,
    RunSummary,
    SheetCell,
    SheetColumn,
    SheetData,
    SheetDiff,
    SheetRow,
    SheetSummary,
)

# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

# FIXTURE: replaced by engine/storage in later todos
_RUNS: tuple[RunSummary, ...] = (
    RunSummary(
        run_id="run_2026_05_18_001",
        servicer="MRC",
        remit_date=date(2026, 5, 15),
        status=RunStatus.COMPLETED,
        created_at=datetime(2026, 5, 18, 1, 23, 45, tzinfo=timezone.utc),
        validators_passed=11,
        validators_failed=1,
    ),
    RunSummary(
        run_id="run_2026_05_17_002",
        servicer="MRC",
        remit_date=date(2026, 5, 14),
        status=RunStatus.COMPLETED,
        created_at=datetime(2026, 5, 17, 18, 2, 11, tzinfo=timezone.utc),
        validators_passed=12,
        validators_failed=0,
    ),
    RunSummary(
        run_id="run_2026_05_16_003",
        servicer="MRC",
        remit_date=date(2026, 5, 13),
        status=RunStatus.COMPLETED,
        created_at=datetime(2026, 5, 16, 17, 50, 0, tzinfo=timezone.utc),
        validators_passed=12,
        validators_failed=0,
    ),
    RunSummary(
        run_id="run_2026_05_15_004",
        servicer="MRC",
        remit_date=date(2026, 5, 12),
        status=RunStatus.FAILED,
        created_at=datetime(2026, 5, 15, 17, 5, 22, tzinfo=timezone.utc),
        validators_passed=8,
        validators_failed=4,
    ),
)


# FIXTURE: replaced by engine/storage in later todos
_SHEET_SUMMARIES: tuple[SheetSummary, ...] = (
    SheetSummary(
        sheet_name="MRC_Summary_check",
        title="MRC Summary Check",
        tab_order=1,
        row_count=1,
        column_count=13,
        highlight_count=2,
    ),
    SheetSummary(
        sheet_name="MRC_General_Check",
        title="MRC General Check",
        tab_order=2,
        row_count=128,
        column_count=33,
        highlight_count=5,
    ),
    SheetSummary(
        sheet_name="MRC_Advance_Check",
        title="MRC Advance Check",
        tab_order=3,
        row_count=128,
        column_count=26,
        highlight_count=3,
    ),
    SheetSummary(
        sheet_name="MRC_ServiceFee_Check",
        title="MRC Service-Fee Check",
        tab_order=4,
        row_count=128,
        column_count=8,
        highlight_count=0,
    ),
    SheetSummary(
        sheet_name="MRC_Adv_Info",
        title="MRC Advance Info",
        tab_order=5,
        row_count=128,
        column_count=10,
        highlight_count=0,
    ),
)


def list_runs(
    *,
    servicer: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[RunSummary], int]:
    """FIXTURE: replaced by engine/storage in later todos.

    Returns the filtered slice plus the unfiltered ``total`` count
    matching the predicate (so the FE can render pagination correctly).
    """
    rows: list[RunSummary] = list(_RUNS)
    if servicer is not None:
        rows = [r for r in rows if r.servicer == servicer]
    if from_date is not None:
        rows = [r for r in rows if r.remit_date >= from_date]
    if to_date is not None:
        rows = [r for r in rows if r.remit_date <= to_date]
    total = len(rows)
    return rows[offset : offset + limit], total


def get_run(run_id: str) -> RunDetail | None:
    """FIXTURE: replaced by engine/storage in later todos."""
    base = next((r for r in _RUNS if r.run_id == run_id), None)
    if base is None:
        # FE-friendly: synthesise a plausible detail for any unknown id so
        # the OpenAPI surface stays exercisable in dev. Real backend will
        # return 404 here.
        base = _RUNS[0].model_copy(update={"run_id": run_id})
    verdict = (
        DiffVerdict.MAJOR_DIFFS
        if base.status is RunStatus.FAILED
        else DiffVerdict.MINOR_DIFFS
        if base.validators_failed > 0
        else DiffVerdict.PASS
    )
    return RunDetail(
        **base.model_dump(),
        sheets=list(_SHEET_SUMMARIES),
        verdict=verdict,
        baseline_run_id="baseline_2026_04_30",
    )


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------


# FIXTURE: replaced by engine/storage in later todos
_ADVANCE_COLUMNS: tuple[SheetColumn, ...] = (
    SheetColumn(id="loan_number", label="Loan Number", dtype="string", is_highlight=False),
    SheetColumn(id="adv_balance_prev", label="Adv Balance (Prev)", dtype="number", is_highlight=False),
    SheetColumn(id="adv_balance_cur", label="Adv Balance (Curr)", dtype="number", is_highlight=False),
    SheetColumn(
        id="diff_adv_bal",
        label="Δ Advance Balance",
        dtype="number",
        is_highlight=True,
    ),
    SheetColumn(id="status", label="Status", dtype="string", is_highlight=False),
)


def list_sheets(run_id: str) -> list[SheetSummary]:
    """FIXTURE: replaced by engine/storage in later todos."""
    del run_id  # all fixture runs share the same MRC sheet set
    return list(_SHEET_SUMMARIES)


def get_sheet(run_id: str, sheet_name: str) -> SheetData | None:
    """FIXTURE: replaced by engine/storage in later todos."""
    summary = next(
        (s for s in _SHEET_SUMMARIES if s.sheet_name == sheet_name), None
    )
    if summary is None:
        return None

    rows: list[SheetRow] = [
        SheetRow(
            row_index=1,
            values={
                "loan_number": "1001",
                "adv_balance_prev": 49500.0,
                "adv_balance_cur": 50000.0,
                "diff_adv_bal": 500.0,
                "status": "current",
            },
        ),
        SheetRow(
            row_index=2,
            values={
                "loan_number": "1002",
                "adv_balance_prev": 32000.0,
                "adv_balance_cur": 32000.0,
                "diff_adv_bal": 0.0,
                "status": "current",
            },
        ),
        SheetRow(
            row_index=3,
            values={
                "loan_number": "1003",
                "adv_balance_prev": 0.0,
                "adv_balance_cur": 18000.0,
                "diff_adv_bal": 18000.0,
                "status": "delinquent",
            },
        ),
    ]
    highlighted = [
        SheetCell(
            row=1,
            column_id="diff_adv_bal",
            cell_ref="D2",
            value=500.0,
            is_highlight=True,
            validator_id="mrc_check_adv_balance",
        ),
        SheetCell(
            row=3,
            column_id="diff_adv_bal",
            cell_ref="D4",
            value=18000.0,
            is_highlight=True,
            validator_id="mrc_check_adv_balance",
        ),
    ]
    return SheetData(
        run_id=run_id,
        sheet_name=sheet_name,
        title=summary.title,
        columns=list(_ADVANCE_COLUMNS),
        rows=rows,
        highlighted_cells=highlighted,
    )


def get_cell(run_id: str, sheet_name: str, cell_ref: str) -> CellDetail | None:
    """FIXTURE: replaced by engine/storage in later todos."""
    sheet = get_sheet(run_id, sheet_name)
    if sheet is None:
        return None
    cell = next(
        (c for c in sheet.highlighted_cells if c.cell_ref == cell_ref),
        None,
    )
    if cell is None:
        # Synthesise a non-highlight cell so the FE can drill down on
        # any address during dev.
        cell = SheetCell(
            row=1,
            column_id="loan_number",
            cell_ref=cell_ref,
            value="1001",
            is_highlight=False,
            validator_id=None,
        )
    provenance = [
        CellProvenance(
            kind=LineageNodeKind.SOURCE,
            id="mrc.portmrcremitloanlevelrecap.adv_balance_prev",
            label="adv_balance_prev",
            detail="Source column on mrc.portmrcremitloanlevelrecap (prev cycle).",
        ),
        CellProvenance(
            kind=LineageNodeKind.SOURCE,
            id="mrc.portmrcremitloanlevelrecap.adv_balance_cur",
            label="adv_balance_cur",
            detail="Source column on mrc.portmrcremitloanlevelrecap (curr cycle).",
        ),
        CellProvenance(
            kind=LineageNodeKind.TRANSFORM,
            id="cte.normalize_balance",
            label="normalize_balance",
            detail="Coerces NULL → 0 before differencing.",
        ),
        CellProvenance(
            kind=LineageNodeKind.VALIDATOR,
            id="mrc_check_adv_balance",
            label="V3 mrc_check_adv_balance",
            detail="Highlights abs(diff_adv_bal) > 0.",
        ),
        CellProvenance(
            kind=LineageNodeKind.FIELD,
            id="MRC_Advance_Check.diff_adv_bal",
            label="diff_adv_bal",
            detail="Output column on MRC_Advance_Check.",
        ),
    ]
    return CellDetail(
        run_id=run_id,
        sheet_name=sheet_name,
        cell=cell,
        computed_expression="diff_adv_bal = adv_balance_cur - adv_balance_prev",
        provenance=provenance,
    )


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------


def get_diff(run_id: str, against: str) -> DiffResponse:
    """FIXTURE: replaced by engine/storage in later todos."""
    sheets = [
        SheetDiff(
            sheet_name="MRC_Summary_check",
            cells=[
                DiffCell(
                    sheet="MRC_Summary_check",
                    cell_ref="C4",
                    column_id="totremit",
                    left=1234.56,
                    right=1234.57,
                    kind=DiffKind.VALUE,
                ),
            ],
            rows_added=0,
            rows_removed=0,
            cells_changed=1,
        ),
        SheetDiff(
            sheet_name="MRC_Advance_Check",
            cells=[
                DiffCell(
                    sheet="MRC_Advance_Check",
                    cell_ref="D4",
                    column_id="diff_adv_bal",
                    left=0.0,
                    right=18000.0,
                    kind=DiffKind.VALUE,
                ),
            ],
            rows_added=0,
            rows_removed=0,
            cells_changed=1,
        ),
    ]
    total = sum(s.cells_changed for s in sheets)
    return DiffResponse(
        run_id=run_id,
        compared_to=against,
        verdict=DiffVerdict.MINOR_DIFFS,
        total_cells_changed=total,
        sheets=sheets,
    )


# ---------------------------------------------------------------------------
# Lineage
# ---------------------------------------------------------------------------


# FIXTURE: replaced by engine/storage in later todos
_LINEAGE_FIELDS: tuple[LineageField, ...] = (
    LineageField(
        field_id="MRC_Advance_Check.diff_adv_bal",
        servicer="MRC",
        sheet="MRC_Advance_Check",
        label="Δ Advance Balance",
    ),
    LineageField(
        field_id="MRC_Summary_check.totremit",
        servicer="MRC",
        sheet="MRC_Summary_check",
        label="Total Remit",
    ),
    LineageField(
        field_id="MRC_General_Check.endbal_diff_remitvsdaily",
        servicer="MRC",
        sheet="MRC_General_Check",
        label="Δ Ending Balance (remit vs daily)",
    ),
)


def list_lineage_fields() -> list[LineageField]:
    """FIXTURE: replaced by engine/storage in later todos."""
    return list(_LINEAGE_FIELDS)


def get_lineage(field_id: str) -> LineageGraph:
    """FIXTURE: replaced by engine/storage in later todos.

    Produces a minimal but real-shaped graph: two backward sources
    flowing through a transform + validator into the requested field,
    plus one forward consumer (the diff report). This is enough for
    the FE to exercise react-flow's layout, node renderer, and edge
    selection logic.
    """
    nodes: list[LineageNode] = [
        LineageNode(
            id="src.adv_balance_prev",
            type=LineageNodeKind.SOURCE,
            data=LineageNodeData(
                label="adv_balance_prev",
                detail="mrc.portmrcremitloanlevelrecap (prev cycle)",
            ),
            position=LineagePosition(x=0.0, y=0.0),
        ),
        LineageNode(
            id="src.adv_balance_cur",
            type=LineageNodeKind.SOURCE,
            data=LineageNodeData(
                label="adv_balance_cur",
                detail="mrc.portmrcremitloanlevelrecap (curr cycle)",
            ),
            position=LineagePosition(x=0.0, y=120.0),
        ),
        LineageNode(
            id="cte.normalize_balance",
            type=LineageNodeKind.TRANSFORM,
            data=LineageNodeData(
                label="normalize_balance",
                detail="NULL → 0 coercion before differencing.",
            ),
            position=LineagePosition(x=220.0, y=60.0),
        ),
        LineageNode(
            id="validator.mrc_check_adv_balance",
            type=LineageNodeKind.VALIDATOR,
            data=LineageNodeData(
                label="V3 mrc_check_adv_balance",
                detail="Highlights abs(diff_adv_bal) > 0.",
            ),
            position=LineagePosition(x=440.0, y=60.0),
        ),
        LineageNode(
            id=field_id,
            type=LineageNodeKind.FIELD,
            data=LineageNodeData(label=field_id, detail="Output field."),
            position=LineagePosition(x=660.0, y=60.0),
        ),
        LineageNode(
            id="sheet.MRC_Advance_Check",
            type=LineageNodeKind.SHEET,
            data=LineageNodeData(
                label="MRC_Advance_Check",
                detail="Downstream consumer sheet.",
            ),
            position=LineagePosition(x=880.0, y=60.0),
        ),
    ]
    edges: list[LineageEdge] = [
        LineageEdge(
            id="e1",
            source="src.adv_balance_prev",
            target="cte.normalize_balance",
            relation=LineageEdgeRelation.READS,
        ),
        LineageEdge(
            id="e2",
            source="src.adv_balance_cur",
            target="cte.normalize_balance",
            relation=LineageEdgeRelation.READS,
        ),
        LineageEdge(
            id="e3",
            source="cte.normalize_balance",
            target="validator.mrc_check_adv_balance",
            relation=LineageEdgeRelation.READS,
        ),
        LineageEdge(
            id="e4",
            source="validator.mrc_check_adv_balance",
            target=field_id,
            relation=LineageEdgeRelation.WRITES,
        ),
        LineageEdge(
            id="e5",
            source=field_id,
            target="sheet.MRC_Advance_Check",
            relation=LineageEdgeRelation.DERIVES,
        ),
    ]
    return LineageGraph(field_id=field_id, nodes=nodes, edges=edges)


__all__ = [
    "get_cell",
    "get_diff",
    "get_lineage",
    "get_run",
    "get_sheet",
    "list_lineage_fields",
    "list_runs",
    "list_sheets",
]
