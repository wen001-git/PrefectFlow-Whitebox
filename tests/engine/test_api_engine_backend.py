"""Verify the API ``engine_backend`` adapter serves live engine output."""

from __future__ import annotations

import importlib
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from whitebox.engine import CTEHarnessSource, Engine


@pytest.fixture()
def live_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("ENGINE_BACKEND", "live")
    # Reload the backend module + the router modules so they re-read
    # the env var and rebuild the live-vs-fixtures dispatch dict at
    # function definition time.
    from whitebox.api.data import engine_backend
    from whitebox.api.routers import runs as runs_router
    from whitebox.api.routers import sheets as sheets_router

    importlib.reload(engine_backend)
    importlib.reload(runs_router)
    importlib.reload(sheets_router)
    from whitebox.api import main as api_main

    importlib.reload(api_main)
    yield TestClient(api_main.app)


def _current_run_id() -> str:
    engine = Engine.bootstrap_mrc()
    from tests.engine.conftest import FIXTURE_DIR

    src = CTEHarnessSource(fixture_dir=FIXTURE_DIR)
    from datetime import date

    result = engine.run(servicer="MRC", remit_date=date(2026, 4, 30), source=src)
    return result.run_id


def test_live_backend_lists_engine_runs(live_client: TestClient) -> None:
    resp = live_client.get("/api/v1/runs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total"] >= 1
    run_ids = [r["run_id"] for r in body["runs"]]
    rid = _current_run_id()
    assert rid in run_ids


def test_live_backend_returns_engine_run_detail(live_client: TestClient) -> None:
    rid = _current_run_id()
    resp = live_client.get(f"/api/v1/runs/{rid}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["run_id"] == rid
    assert body["servicer"] == "MRC"
    assert len(body["sheets"]) == 5


def test_live_backend_returns_engine_sheet(live_client: TestClient) -> None:
    rid = _current_run_id()
    resp = live_client.get(f"/api/v1/runs/{rid}/sheets/MRC_ServiceFee_Check")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["sheet_name"] == "MRC_ServiceFee_Check"
    assert isinstance(body["columns"], list)
    assert len(body["columns"]) > 0


def test_default_backend_remains_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENGINE_BACKEND", raising=False)
    from whitebox.api.data import engine_backend

    importlib.reload(engine_backend)
    assert engine_backend.backend_name() == "fixtures"
    assert engine_backend.use_live_backend() is False
