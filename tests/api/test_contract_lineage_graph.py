"""Contract test: lineage graph shape is react-flow consumable.

react-flow's minimal node contract is ``{id, position: {x, y}, data}``
and its edge contract is ``{id, source, target}``. We assert both, plus
that every edge endpoint exists in the node set.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_lineage_graph_is_react_flow_shaped(client: TestClient) -> None:
    resp = client.get("/api/v1/lineage/fields/MRC_Advance_Check.diff_adv_bal")
    assert resp.status_code == 200
    body = resp.json()

    assert body["field_id"] == "MRC_Advance_Check.diff_adv_bal"
    nodes = body["nodes"]
    edges = body["edges"]
    assert nodes and edges

    node_ids: set[str] = set()
    for node in nodes:
        # react-flow required keys
        assert {"id", "position", "data", "type"}.issubset(node.keys())
        assert isinstance(node["id"], str) and node["id"]
        pos = node["position"]
        assert isinstance(pos, dict)
        assert isinstance(pos["x"], (int, float))
        assert isinstance(pos["y"], (int, float))
        data = node["data"]
        assert isinstance(data, dict)
        assert isinstance(data["label"], str) and data["label"]
        node_ids.add(node["id"])

    for edge in edges:
        assert {"id", "source", "target", "relation"}.issubset(edge.keys())
        assert edge["source"] in node_ids, f"dangling source {edge['source']}"
        assert edge["target"] in node_ids, f"dangling target {edge['target']}"


def test_lineage_graph_node_kinds_are_enumerated(client: TestClient) -> None:
    resp = client.get("/api/v1/lineage/fields/MRC_Advance_Check.diff_adv_bal")
    body = resp.json()
    allowed = {"source", "transform", "validator", "sheet", "field"}
    for node in body["nodes"]:
        assert node["type"] in allowed
    allowed_relations = {"reads", "writes", "derives"}
    for edge in body["edges"]:
        assert edge["relation"] in allowed_relations
