from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import DiffResponse


def test_get_diff_default_against_baseline(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/diff")
    assert resp.status_code == 200
    diff = DiffResponse.model_validate(resp.json())
    assert diff.run_id == "run_xyz"
    assert diff.compared_to == "baseline"
    assert diff.verdict.value in {"PASS", "MINOR_DIFFS", "MAJOR_DIFFS", "ERROR"}
    assert diff.sheets
    assert diff.total_cells_changed == sum(s.cells_changed for s in diff.sheets)
    first_cell = diff.sheets[0].cells[0]
    assert first_cell.kind.value in {"value", "missing_left", "missing_right", "type", "format"}


def test_get_diff_against_override(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/runs/run_xyz/diff", params={"against": "run_abc"}
    )
    assert resp.status_code == 200
    assert DiffResponse.model_validate(resp.json()).compared_to == "run_abc"
