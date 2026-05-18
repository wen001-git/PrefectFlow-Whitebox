from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import RunDetail, RunListResponse


def test_list_runs_returns_pagination_envelope(client: TestClient) -> None:
    resp = client.get("/api/v1/runs")
    assert resp.status_code == 200
    body = RunListResponse.model_validate(resp.json())
    assert body.pagination.total >= 1
    assert body.pagination.limit == 50
    assert body.pagination.offset == 0
    assert len(body.runs) <= body.pagination.limit
    first = body.runs[0]
    assert first.servicer
    assert first.run_id
    assert first.validators_passed >= 0
    assert first.validators_failed >= 0


def test_list_runs_filters_by_servicer(client: TestClient) -> None:
    resp = client.get("/api/v1/runs", params={"servicer": "MRC"})
    assert resp.status_code == 200
    body = RunListResponse.model_validate(resp.json())
    assert all(r.servicer == "MRC" for r in body.runs)


def test_list_runs_filters_by_date_range(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/runs",
        params={"from_date": "2026-05-14", "to_date": "2026-05-15"},
    )
    assert resp.status_code == 200
    body = RunListResponse.model_validate(resp.json())
    assert body.pagination.total >= 1
    for r in body.runs:
        assert r.remit_date.isoformat() >= "2026-05-14"
        assert r.remit_date.isoformat() <= "2026-05-15"


def test_get_run_returns_full_detail(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_2026_05_18_001")
    assert resp.status_code == 200
    detail = RunDetail.model_validate(resp.json())
    assert detail.run_id == "run_2026_05_18_001"
    assert detail.sheets, "run detail should embed sheet summaries"
    assert detail.verdict.value in {"PASS", "MINOR_DIFFS", "MAJOR_DIFFS", "ERROR"}
    # baseline_run_id is optional; if present must be a string
    if detail.baseline_run_id is not None:
        assert isinstance(detail.baseline_run_id, str)
