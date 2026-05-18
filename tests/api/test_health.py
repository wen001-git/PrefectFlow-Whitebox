from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox import __version__


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "ok", "version": __version__}
