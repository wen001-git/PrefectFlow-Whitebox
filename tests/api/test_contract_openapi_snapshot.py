"""OpenAPI snapshot contract test.

The snapshot at ``tests/api/openapi_snapshot.json`` is the source of
truth for the public API surface produced by :mod:`whitebox.api.main`.
This test asserts that the live ``/openapi.json`` payload is byte-for-
byte equal to the snapshot (after deterministic key sorting).

If the change is intentional (you added an endpoint or extended a
schema in a backwards-compatible way), refresh the snapshot with::

    .venv\\Scripts\\python.exe -m pytest tests/api/test_contract_openapi_snapshot.py \\
        --snapshot-update

Breaking changes (renamed/removed paths, dropped fields, narrowed
types) require an ADR before the snapshot is refreshed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

SNAPSHOT_PATH = Path(__file__).with_name("openapi_snapshot.json")

# Endpoints we promise to the FE; if any of these disappears the
# snapshot diff would catch it too, but the explicit list yields a
# better failure message.
EXPECTED_PATHS: tuple[str, ...] = (
    "/health",
    "/api/v1/runs",
    "/api/v1/runs/{run_id}",
    "/api/v1/runs/{run_id}/sheets",
    "/api/v1/runs/{run_id}/sheets/{sheet_name}",
    "/api/v1/runs/{run_id}/sheets/{sheet_name}/cells/{cell_ref}",
    "/api/v1/runs/{run_id}/diff",
    "/api/v1/runs/{run_id}/export",
    "/api/v1/lineage/fields",
    "/api/v1/lineage/fields/{field_id}",
)


def _canonical(obj: Any) -> str:
    """Sort all keys recursively so the snapshot diff is stable."""
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def _fetch_spec(client: TestClient) -> dict[str, Any]:
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec: dict[str, Any] = resp.json()
    return spec


def test_openapi_publishes_all_expected_paths(client: TestClient) -> None:
    spec = _fetch_spec(client)
    paths = spec["paths"]
    for path in EXPECTED_PATHS:
        assert path in paths, f"missing {path} in OpenAPI"


def test_openapi_snapshot(client: TestClient, request: pytest.FixtureRequest) -> None:
    spec = _fetch_spec(client)
    actual = _canonical(spec)

    update = (
        request.config.getoption("--snapshot-update", default=False)
        or os.environ.get("UPDATE_OPENAPI_SNAPSHOT") == "1"
    )

    if update or not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.write_text(actual, encoding="utf-8")
        pytest.skip(f"OpenAPI snapshot written to {SNAPSHOT_PATH}")

    expected = SNAPSHOT_PATH.read_text(encoding="utf-8")
    assert actual == expected, (
        "OpenAPI surface drifted from snapshot. If the change is intentional "
        "and backwards-compatible, re-run with --snapshot-update."
    )
