"""Run listing / detail router (stub).

TODO(d-api-contracts): replace fixture data with real registry/engine
lookups against `runs/` artifacts and the registry metadata.
"""

from __future__ import annotations

from fastapi import APIRouter

from whitebox.api.schemas import RunDetail, RunListResponse, RunSummary

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


_FIXTURE_RUNS: list[RunSummary] = [
    RunSummary(
        run_id="run_2026_05_18_001",
        servicer="MRC",
        remit_date="2026-05-15",
        status="completed",
        created_at="2026-05-18T01:23:45Z",
    ),
    RunSummary(
        run_id="run_2026_05_17_002",
        servicer="MRC",
        remit_date="2026-05-14",
        status="completed",
        created_at="2026-05-17T18:02:11Z",
    ),
]


@router.get("", response_model=RunListResponse)
def list_runs() -> RunListResponse:
    return RunListResponse(runs=_FIXTURE_RUNS, total=len(_FIXTURE_RUNS))


@router.get("/{run_id}", response_model=RunDetail)
def get_run(run_id: str) -> RunDetail:
    base = _FIXTURE_RUNS[0]
    return RunDetail(
        run_id=run_id,
        servicer=base.servicer,
        remit_date=base.remit_date,
        status=base.status,
        created_at=base.created_at,
        sheets=["MRC_Summary", "Loan_Detail", "Adjustments", "Exceptions", "Trailer"],
        validators_passed=11,
        validators_failed=1,
    )
