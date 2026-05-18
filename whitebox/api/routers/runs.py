"""Run listing / detail router.

Backed by the fixture provider in :mod:`whitebox.api.data.fixtures`.
The engine / storage wiring lands in a later todo; this router owns
the public HTTP contract only.
"""

from __future__ import annotations

from datetime import date
from types import ModuleType
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from whitebox.api.data import engine_backend, fixtures
from whitebox.api.schemas import Pagination, RunDetail, RunListResponse

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


def _backend() -> ModuleType:
    """Return the active data provider — live engine or fixtures."""
    return engine_backend if engine_backend.use_live_backend() else fixtures


@router.get("", response_model=RunListResponse, summary="List runs")
def list_runs(
    servicer: Annotated[str | None, Query(description="Filter by servicer id.")] = None,
    from_date: Annotated[date | None, Query(description="Inclusive lower bound on remit_date.")] = None,
    to_date: Annotated[date | None, Query(description="Inclusive upper bound on remit_date.")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RunListResponse:
    runs, total = _backend().list_runs(
        servicer=servicer,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return RunListResponse(
        runs=runs,
        pagination=Pagination(total=total, limit=limit, offset=offset),
    )


@router.get("/{run_id}", response_model=RunDetail, summary="Get one run")
def get_run(run_id: str) -> RunDetail:
    detail: RunDetail | None = _backend().get_run(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"run {run_id!r} not found")
    return detail
