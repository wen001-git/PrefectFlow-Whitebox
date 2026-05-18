from __future__ import annotations

from fastapi.testclient import TestClient


def test_get_sheet_shape(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/sheets/MRC_Summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"] == "run_xyz"
    assert body["sheet_name"] == "MRC_Summary"
    assert isinstance(body["columns"], list) and body["columns"]
    assert isinstance(body["rows"], list) and body["rows"]
    assert isinstance(body["cells"], list)
    # rows should be column-keyed dicts
    assert set(body["columns"]).issubset(set(body["rows"][0].keys()))
