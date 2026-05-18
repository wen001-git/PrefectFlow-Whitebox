from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_diff_shape(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/diff")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"] == "run_xyz"
    assert body["compared_to"] == "baseline"
    assert body["verdict"] in {"PASS", "MINOR_DIFFS", "MAJOR_DIFFS", "ERROR"}
    assert isinstance(body["diffs"], list) and body["diffs"]
    entry = body["diffs"][0]
    for key in ("sheet", "cell", "left", "right", "kind"):
        assert key in entry


def test_get_diff_compared_to_override(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/diff", params={"compared_to": "run_abc"})
    assert resp.status_code == 200
    assert resp.json()["compared_to"] == "run_abc"
