"""XLSX export router.

Returns HTTP 501 with a structured :class:`ErrorResponse` body until
the renderer wiring (later todo) lands. The eventual success body is
declared by :class:`whitebox.api.schemas.ExportResponse` so the
OpenAPI surface already advertises the contract.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from whitebox.api.schemas import ErrorDetail, ErrorResponse, ExportResponse

router = APIRouter(prefix="/api/v1/runs", tags=["export"])


@router.get(
    "/{run_id}/export",
    summary="Export a run as XLSX",
    responses={
        200: {"model": ExportResponse},
        501: {"model": ErrorResponse},
    },
)
def export_run(
    run_id: str,
    format: Annotated[Literal["xlsx"], Query()] = "xlsx",
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(
            code="NOT_IMPLEMENTED",
            message=(
                f"export for run {run_id} (format={format}) is not yet implemented"
            ),
            hint=(
                "engine + renderer wiring is scheduled by a later todo; "
                "contract is declared via ExportResponse"
            ),
        )
    )
    return JSONResponse(status_code=501, content=body.model_dump())
