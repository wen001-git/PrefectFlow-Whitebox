"""Live-engine backend for the FastAPI routers.

Adapts :class:`whitebox.engine.RunResult` to the pydantic schemas in
:mod:`whitebox.api.schemas`. Enabled by setting the environment
variable ``ENGINE_BACKEND=live`` before the FastAPI app boots; the
default (``ENGINE_BACKEND=fixtures``) preserves the existing static
FE-friendly fixtures.

This module is intentionally *thin*: each `get_*` function here has a
1:1 counterpart in :mod:`whitebox.api.data.fixtures`. The router
chooses between the two via :func:`backend_name`.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Literal

from whitebox.api.schemas import (
    DiffVerdict,
    RunDetail,
    RunStatus,
    RunSummary,
    SheetCell,
    SheetColumn,
    SheetData,
    SheetRow,
    SheetSummary,
)
from whitebox.engine import (
    CTEHarnessSource,
    Engine,
    RunResult,
    SheetResult,
    SheetVerdict,
)

__all__ = [
    "backend_name",
    "get_run",
    "get_sheet",
    "list_runs",
    "list_sheets",
    "use_live_backend",
]


_BACKEND_ENV = "ENGINE_BACKEND"
_LIVE = "live"
_FIXTURES = "fixtures"


def backend_name() -> str:
    """Return the configured backend name (``"fixtures"`` or ``"live"``)."""
    return os.environ.get(_BACKEND_ENV, _FIXTURES)


def use_live_backend() -> bool:
    """``True`` when the API should serve engine output instead of fixtures."""
    return backend_name() == _LIVE


# ---------------------------------------------------------------------------
# Engine bootstrap (deterministic, single run per process by default).
# ---------------------------------------------------------------------------


def _default_fixture_dir() -> Path:
    # whitebox/api/data/engine_backend.py → up to repo root → tests/fixtures/cte_harness
    return (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "fixtures"
        / "cte_harness"
    )


@lru_cache(maxsize=1)
def _bootstrapped_engine() -> Engine:
    return Engine.bootstrap_mrc()


@lru_cache(maxsize=8)
def _cached_run(servicer: str, remit_iso: str) -> RunResult:
    engine = _bootstrapped_engine()
    source = CTEHarnessSource(fixture_dir=_default_fixture_dir())
    return engine.run(
        servicer=servicer,
        remit_date=date.fromisoformat(remit_iso),
        source=source,
    )


# ---------------------------------------------------------------------------
# Verdict + status mapping.
# ---------------------------------------------------------------------------


def _verdict_to_api(result: RunResult) -> DiffVerdict:
    """Map engine OverallVerdict → API DiffVerdict."""
    mapping = {
        "PASS": DiffVerdict.PASS,
        "WARN": DiffVerdict.MINOR_DIFFS,
        "DEGRADED": DiffVerdict.MINOR_DIFFS,
        "ERROR": DiffVerdict.MAJOR_DIFFS,
    }
    return mapping.get(result.overall_verdict.value, DiffVerdict.ERROR)


def _summary_from_result(result: RunResult) -> RunSummary:
    passed = sum(1 for s in result.sheets if s.verdict is SheetVerdict.PASS)
    failed = sum(
        1
        for s in result.sheets
        if s.verdict in (SheetVerdict.WARN, SheetVerdict.ERROR, SheetVerdict.DEGRADED)
    )
    return RunSummary(
        run_id=result.run_id,
        servicer=result.servicer,
        remit_date=result.remit_date,
        status=RunStatus.COMPLETED,
        created_at=_aware(result.created_at),
        validators_passed=passed,
        validators_failed=failed,
    )


def _aware(dt: datetime) -> datetime:
    """Ensure tz-aware UTC datetime (engine emits UTC already)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _sheet_summary_from_result(sheet: SheetResult) -> SheetSummary:
    spec = sheet.sheet_model
    return SheetSummary(
        sheet_name=sheet.sheet_name,
        title=sheet.sheet_name,
        tab_order=0,
        row_count=sheet.row_count,
        column_count=len(spec.columns),
        highlight_count=sheet.highlight_count,
    )


def _sheet_data_from_result(
    result: RunResult, sheet: SheetResult
) -> SheetData:
    spec = sheet.sheet_model
    columns = [
        SheetColumn(
            id=c.key,
            label=c.header_label,
            dtype=_dtype_for(c.data_type),
            is_highlight=c.highlight,
        )
        for c in spec.columns
    ]
    rows: list[SheetRow] = []
    highlighted: list[SheetCell] = []
    for row_idx, row in enumerate(spec.rows, start=1):
        values: dict[str, str | int | float | bool | None] = {}
        for col_idx, (col, cell) in enumerate(zip(spec.columns, row.cells, strict=True), start=1):
            api_value = _coerce_cell_value(cell.value)
            values[col.key] = api_value
            if "diff" in cell.style.classes:
                from openpyxl.utils import get_column_letter

                highlighted.append(
                    SheetCell(
                        row=row_idx + 1,
                        column_id=col.key,
                        cell_ref=f"{get_column_letter(col_idx)}{row_idx + 1}",
                        value=api_value,
                        is_highlight=True,
                        validator_id=sheet.validator_id,
                    )
                )
        rows.append(SheetRow(row_index=row_idx, values=values))

    return SheetData(
        run_id=result.run_id,
        sheet_name=sheet.sheet_name,
        title=sheet.sheet_name,
        columns=columns,
        rows=rows,
        highlighted_cells=highlighted,
    )


def _dtype_for(data_type: str) -> Literal["string", "number", "integer", "boolean", "date"]:
    mapping: dict[str, Literal["string", "number", "integer", "boolean", "date"]] = {
        "str": "string",
        "money": "number",
        "float": "number",
        "int": "integer",
        "date": "date",
        "percentage": "number",
    }
    return mapping.get(data_type, "string")


def _coerce_cell_value(value: object) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


# ---------------------------------------------------------------------------
# Public surface — mirrors whitebox.api.data.fixtures.
# ---------------------------------------------------------------------------


_DEFAULT_REMIT_DATE = "2026-04-30"
_DEFAULT_SERVICER = "MRC"


def _current_run() -> RunResult:
    return _cached_run(_DEFAULT_SERVICER, _DEFAULT_REMIT_DATE)


def list_runs(
    *,
    servicer: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[RunSummary], int]:
    result = _current_run()
    summary = _summary_from_result(result)
    rows = [summary]
    if servicer is not None:
        rows = [r for r in rows if r.servicer == servicer]
    if from_date is not None:
        rows = [r for r in rows if r.remit_date >= from_date]
    if to_date is not None:
        rows = [r for r in rows if r.remit_date <= to_date]
    total = len(rows)
    return rows[offset : offset + limit], total


def get_run(run_id: str) -> RunDetail | None:
    result = _current_run()
    if result.run_id != run_id:
        return None
    base = _summary_from_result(result)
    sheets = [_sheet_summary_from_result(s) for s in result.sheets]
    return RunDetail(
        **base.model_dump(),
        sheets=sheets,
        verdict=_verdict_to_api(result),
        baseline_run_id=None,
    )


def list_sheets(run_id: str) -> list[SheetSummary]:
    result = _current_run()
    del run_id  # live engine only knows about the cached current run
    return [_sheet_summary_from_result(s) for s in result.sheets]


def get_sheet(run_id: str, sheet_name: str) -> SheetData | None:
    result = _current_run()
    if result.run_id != run_id:
        return None
    for sheet in result.sheets:
        if sheet.sheet_name == sheet_name:
            return _sheet_data_from_result(result, sheet)
    return None
