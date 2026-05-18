"""Pagination contract test for /api/v1/runs.

Verifies that ``limit`` and ``offset`` deterministically slice the
result set and that ``total`` reflects the unfiltered match count.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import RunListResponse


def _fetch(client: TestClient, **params: object) -> RunListResponse:
    resp = client.get("/api/v1/runs", params=params)
    assert resp.status_code == 200, resp.text
    return RunListResponse.model_validate(resp.json())


def test_pagination_limit_caps_returned_runs(client: TestClient) -> None:
    body = _fetch(client, limit=2, offset=0)
    assert len(body.runs) == 2
    assert body.pagination.limit == 2
    assert body.pagination.offset == 0
    assert body.pagination.total >= 2


def test_pagination_offset_skips_runs(client: TestClient) -> None:
    page1 = _fetch(client, limit=2, offset=0)
    page2 = _fetch(client, limit=2, offset=2)
    ids1 = [r.run_id for r in page1.runs]
    ids2 = [r.run_id for r in page2.runs]
    assert set(ids1).isdisjoint(set(ids2))
    assert page1.pagination.total == page2.pagination.total


def test_pagination_rejects_invalid_limit(client: TestClient) -> None:
    resp = client.get("/api/v1/runs", params={"limit": 0})
    assert resp.status_code == 422
    resp = client.get("/api/v1/runs", params={"limit": 1000})
    assert resp.status_code == 422


def test_pagination_rejects_negative_offset(client: TestClient) -> None:
    resp = client.get("/api/v1/runs", params={"offset": -1})
    assert resp.status_code == 422


def test_pagination_total_unchanged_across_pages(client: TestClient) -> None:
    a = _fetch(client, limit=1, offset=0)
    b = _fetch(client, limit=1, offset=1)
    assert a.pagination.total == b.pagination.total
