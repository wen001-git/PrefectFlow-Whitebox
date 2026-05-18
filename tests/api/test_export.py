from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import ErrorResponse


def test_export_returns_501_structured_error(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/export")
    assert resp.status_code == 501
    body = ErrorResponse.model_validate(resp.json())
    assert body.error.code == "NOT_IMPLEMENTED"
    assert "run_xyz" in body.error.message
    assert body.error.hint


def test_export_accepts_format_query(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/export", params={"format": "xlsx"})
    assert resp.status_code == 501


def test_export_rejects_unknown_format(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/export", params={"format": "pdf"})
    # fastapi/pydantic Literal validation produces a 422 for unknown enum values
    assert resp.status_code == 422
