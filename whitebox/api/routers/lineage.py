"""Field-lineage router.

Endpoints
---------
- ``GET /api/v1/lineage/fields`` — list lineage-known output fields.
- ``GET /api/v1/lineage/fields/{field_id}`` — backward + forward
  lineage graph in react-flow node/edge shape.
"""

from __future__ import annotations

from fastapi import APIRouter

from whitebox.api.data import fixtures
from whitebox.api.schemas import LineageFieldListResponse, LineageGraph

router = APIRouter(prefix="/api/v1/lineage", tags=["lineage"])


@router.get(
    "/fields",
    response_model=LineageFieldListResponse,
    summary="List lineage-known fields",
)
def list_fields() -> LineageFieldListResponse:
    return LineageFieldListResponse(fields=fixtures.list_lineage_fields())


@router.get(
    "/fields/{field_id}",
    response_model=LineageGraph,
    summary="Backward + forward lineage for one field",
)
def get_field_lineage(field_id: str) -> LineageGraph:
    return fixtures.get_lineage(field_id)
