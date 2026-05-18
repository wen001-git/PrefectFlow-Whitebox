from __future__ import annotations

from fastapi.testclient import TestClient

from whitebox.api.schemas import CellDetail, SheetData, SheetListResponse


def test_list_sheets_returns_typed_summaries(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/sheets")
    assert resp.status_code == 200
    body = SheetListResponse.model_validate(resp.json())
    assert body.run_id == "run_xyz"
    assert body.sheets
    names = {s.sheet_name for s in body.sheets}
    assert "MRC_Advance_Check" in names


def test_get_sheet_returns_columns_and_rows(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/sheets/MRC_Advance_Check")
    assert resp.status_code == 200
    sheet = SheetData.model_validate(resp.json())
    assert sheet.run_id == "run_xyz"
    assert sheet.sheet_name == "MRC_Advance_Check"
    assert sheet.columns and sheet.rows
    col_ids = {c.id for c in sheet.columns}
    # every row uses column-id keys
    for row in sheet.rows:
        assert set(row.values.keys()).issubset(col_ids)
    # at least one highlight column is flagged for this sheet
    assert any(c.is_highlight for c in sheet.columns)


def test_get_sheet_unknown_returns_404(client: TestClient) -> None:
    resp = client.get("/api/v1/runs/run_xyz/sheets/DoesNotExist")
    assert resp.status_code == 404


def test_get_cell_returns_provenance(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/runs/run_xyz/sheets/MRC_Advance_Check/cells/D2"
    )
    assert resp.status_code == 200
    detail = CellDetail.model_validate(resp.json())
    assert detail.cell.cell_ref == "D2"
    assert detail.provenance, "cell detail should embed lineage provenance"
    kinds = {p.kind.value for p in detail.provenance}
    # production contract: at least one source and one validator step
    assert "source" in kinds
    assert "validator" in kinds
