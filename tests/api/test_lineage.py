from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import LineageFieldListResponse, LineageGraph


def test_list_lineage_fields(client: TestClient) -> None:
    resp = client.get("/api/v1/lineage/fields")
    assert resp.status_code == 200
    body = LineageFieldListResponse.model_validate(resp.json())
    assert body.fields
    field_ids = {f.field_id for f in body.fields}
    assert "MRC_Advance_Check.diff_adv_bal" in field_ids


def test_get_lineage_graph_typed(client: TestClient) -> None:
    resp = client.get("/api/v1/lineage/fields/MRC_Advance_Check.diff_adv_bal")
    assert resp.status_code == 200
    graph = LineageGraph.model_validate(resp.json())
    assert graph.field_id == "MRC_Advance_Check.diff_adv_bal"
    assert graph.nodes
    assert graph.edges
    kinds = {n.type.value for n in graph.nodes}
    # backward + forward lineage must include sources, a validator, and the field itself
    assert {"source", "validator", "field"}.issubset(kinds)
