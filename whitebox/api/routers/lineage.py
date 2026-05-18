"""Field-lineage router (stub).

TODO(d-api-contracts): build from registry metadata + validator graph.
"""

from __future__ import annotations

from fastapi import APIRouter

from whitebox.api.schemas import LineageEdge, LineageNode, LineageResponse

router = APIRouter(prefix="/api/v1/lineage", tags=["lineage"])


@router.get("/{field_id}", response_model=LineageResponse)
def get_lineage(field_id: str) -> LineageResponse:
    nodes = [
        LineageNode(id="src.loan_balance", kind="source", label="loan_balance"),
        LineageNode(id="cte.normalize", kind="transform", label="normalize_balance"),
        LineageNode(id=field_id, kind="output", label=field_id),
    ]
    edges = [
        LineageEdge(source="src.loan_balance", target="cte.normalize", relation="reads"),
        LineageEdge(source="cte.normalize", target=field_id, relation="writes"),
    ]
    return LineageResponse(field_id=field_id, nodes=nodes, edges=edges)
