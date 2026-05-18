"""Run-vs-baseline diff router (stub).

TODO(d-api-contracts): wrap tools/xlsx_diff.py output.
"""

from __future__ import annotations

from fastapi import APIRouter

from whitebox.api.schemas import DiffEntry, DiffResponse

router = APIRouter(prefix="/api/v1/runs", tags=["diff"])


@router.get("/{run_id}/diff", response_model=DiffResponse)
def get_diff(run_id: str, compared_to: str = "baseline") -> DiffResponse:
    diffs = [
        DiffEntry(sheet="MRC_Summary", cell="C4", left=1234.56, right=1234.57, kind="value"),
        DiffEntry(
            sheet="Loan_Detail",
            cell="F12",
            left="current",
            right="delinquent",
            kind="value",
        ),
    ]
    return DiffResponse(
        run_id=run_id,
        compared_to=compared_to,
        verdict="MINOR_DIFFS",
        diffs=diffs,
    )
