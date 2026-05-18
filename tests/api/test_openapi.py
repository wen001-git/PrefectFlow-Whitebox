from __future__ import annotations

from fastapi.testclient import TestClient


def test_openapi_published_with_all_routes(client: TestClient) -> None:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.json()
    assert spec["openapi"].startswith("3.")
    paths = spec["paths"]

    expected = [
        "/health",
        "/api/v1/runs",
        "/api/v1/runs/{run_id}",
        "/api/v1/runs/{run_id}/sheets/{sheet_name}",
        "/api/v1/runs/{run_id}/diff",
        "/api/v1/runs/{run_id}/export",
        "/api/v1/lineage/{field_id}",
    ]
    for path in expected:
        assert path in paths, f"missing {path} in OpenAPI"
