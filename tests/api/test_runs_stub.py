from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_runs_shape(client: TestClient) -> None:
    resp = client.get("/api/v1/runs")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"runs", "total"}
    assert body["total"] == len(body["runs"])
    assert body["total"] >= 1
    first = body["runs"][0]
    for key in ("run_id", "servicer", "remit_date", "status", "created_at"):
        assert key in first


def test_get_run_shape(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz")
    assert resp.status_code == 200
    body = resp.json()
    for key in (
        "run_id",
        "servicer",
        "remit_date",
        "status",
        "created_at",
        "sheets",
        "validators_passed",
        "validators_failed",
    ):
        assert key in body
    assert body["run_id"] == "run_xyz"
    assert isinstance(body["sheets"], list)
    assert isinstance(body["validators_passed"], int)
