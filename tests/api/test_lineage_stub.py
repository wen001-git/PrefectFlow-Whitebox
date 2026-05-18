from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_lineage_shape(client: TestClient) -> None:
    resp = client.get("/api/v1/lineage/mrc.summary.net_remit")
    assert resp.status_code == 200
    body = resp.json()
    assert body["field_id"] == "mrc.summary.net_remit"
    assert isinstance(body["nodes"], list) and body["nodes"]
    assert isinstance(body["edges"], list) and body["edges"]
    node_ids = {n["id"] for n in body["nodes"]}
    for edge in body["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
        assert {"source", "target", "relation"}.issubset(edge.keys())
