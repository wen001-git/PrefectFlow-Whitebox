"""Per-sheet drill-down router.

Endpoints
---------
- ``GET /api/v1/runs/{run_id}/sheets`` — list sheet summaries
- ``GET /api/v1/runs/{run_id}/sheets/{sheet_name}`` — sheet contents
- ``GET /api/v1/runs/{run_id}/sheets/{sheet_name}/cells/{cell_ref}`` —
  one cell with provenance (powers the F1 drill-down panel).
"""

from __future__ import annotations

from types import ModuleType

from fastapi import APIRouter, HTTPException

from whitebox.api.data import engine_backend, fixtures
from whitebox.api.schemas import CellDetail, SheetData, SheetListResponse

router = APIRouter(prefix="/api/v1/runs", tags=["sheets"])


def _backend() -> ModuleType:
    return engine_backend if engine_backend.use_live_backend() else fixtures


@router.get(
    "/{run_id}/sheets",
    response_model=SheetListResponse,
    summary="List sheets for a run",
)
def list_sheets(run_id: str) -> SheetListResponse:
    return SheetListResponse(run_id=run_id, sheets=_backend().list_sheets(run_id))


@router.get(
    "/{run_id}/sheets/{sheet_name}",
    response_model=SheetData,
    summary="Get one sheet's contents",
)
def get_sheet(run_id: str, sheet_name: str) -> SheetData:
    data: SheetData | None = _backend().get_sheet(run_id, sheet_name)
    if data is None:
        raise HTTPException(
            status_code=404, detail=f"sheet {sheet_name!r} not found on run {run_id!r}"
        )
    return data


@router.get(
    "/{run_id}/sheets/{sheet_name}/cells/{cell_ref}",
    response_model=CellDetail,
    summary="Get one cell with provenance",
)
def get_cell(run_id: str, sheet_name: str, cell_ref: str) -> CellDetail:
    # Cell-level drill-down is still fixture-only (engine_backend does
    # not synthesise provenance graphs yet — that lands with the next
    # lineage todo).
    detail = fixtures.get_cell(run_id, sheet_name, cell_ref)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"cell {cell_ref!r} not found on sheet {sheet_name!r} "
                f"of run {run_id!r}"
            ),
        )
    return detail
