"""Per-sheet drill-down router (stub).

TODO(d-api-contracts): wire to whitebox.sheets builders + renderer output.
"""

from __future__ import annotations

from fastapi import APIRouter

from whitebox.api.schemas import SheetCell, SheetResponse

router = APIRouter(prefix="/api/v1/runs", tags=["sheets"])


@router.get("/{run_id}/sheets/{sheet_name}", response_model=SheetResponse)
def get_sheet(run_id: str, sheet_name: str) -> SheetResponse:
    columns = ["loan_id", "principal", "interest", "status"]
    rows = [
        {"loan_id": "L0001", "principal": 100000.0, "interest": 4500.0, "status": "current"},
        {"loan_id": "L0002", "principal": 75000.0, "interest": 3100.0, "status": "current"},
    ]
    cells = [
        SheetCell(row=1, col="A", value="L0001"),
        SheetCell(row=1, col="B", value=100000.0),
    ]
    return SheetResponse(
        run_id=run_id,
        sheet_name=sheet_name,
        columns=columns,
        rows=rows,
        cells=cells,
    )
