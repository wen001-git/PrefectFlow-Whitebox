"""Run-vs-run XLSX diff router.

Returns the xlsx_diff-shaped report comparing ``run_id`` against
``against`` (the other run id supplied as a query parameter).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from whitebox.api.data import fixtures
from whitebox.api.schemas import DiffResponse

router = APIRouter(prefix="/api/v1/runs", tags=["diff"])


@router.get(
    "/{run_id}/diff",
    response_model=DiffResponse,
    summary="Diff two runs",
)
def get_diff(
    run_id: str,
    against: Annotated[
        str,
        Query(description="Other run id to diff against (or 'baseline')."),
    ] = "baseline",
) -> DiffResponse:
    return fixtures.get_diff(run_id, against)
