from __future__ import annotations

from fastapi.testclient import TestClient


def test_export_returns_501_structured(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/export")
    assert resp.status_code == 501
    body = resp.json()
    assert "error" in body
    err = body["error"]
    assert err["code"] == "NOT_IMPLEMENTED"
    assert "run_xyz" in err["message"]
    assert err.get("hint")
