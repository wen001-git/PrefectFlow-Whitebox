"""XLSX export router (stub).

Returns HTTP 501 with a structured error until the renderer wiring
(d-api-contracts + downstream) lands.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from whitebox.api.schemas import ErrorDetail, ErrorResponse

router = APIRouter(prefix="/api/v1/runs", tags=["export"])


@router.get(
    "/{run_id}/export",
    responses={501: {"model": ErrorResponse}},
)
def export_run(run_id: str) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(
            code="NOT_IMPLEMENTED",
            message=f"export for run {run_id} is not yet implemented",
            hint="tracked by d-api-contracts; renderer wiring pending",
        )
    )
    return JSONResponse(status_code=501, content=body.model_dump())
