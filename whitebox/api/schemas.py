"""Pydantic response schemas for the FastAPI skeleton.

These shapes are intentionally minimal but plausible: FE devs can build
typed clients against them today, and d-api-contracts will extend them
without breaking the field names already in use.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.0.1"])


class RunSummary(BaseModel):
    run_id: str
    servicer: str
    remit_date: str
    status: str
    created_at: str


class RunListResponse(BaseModel):
    runs: list[RunSummary]
    total: int


class RunDetail(RunSummary):
    sheets: list[str]
    validators_passed: int
    validators_failed: int


class SheetCell(BaseModel):
    row: int
    col: str
    value: Any = None


class SheetResponse(BaseModel):
    run_id: str
    sheet_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    cells: list[SheetCell] = Field(default_factory=list)


class DiffEntry(BaseModel):
    sheet: str
    cell: str
    left: Any = None
    right: Any = None
    kind: str


class DiffResponse(BaseModel):
    run_id: str
    compared_to: str
    verdict: str
    diffs: list[DiffEntry]


class LineageNode(BaseModel):
    id: str
    kind: str
    label: str


class LineageEdge(BaseModel):
    source: str
    target: str
    relation: str


class LineageResponse(BaseModel):
    field_id: str
    nodes: list[LineageNode]
    edges: list[LineageEdge]


class ErrorDetail(BaseModel):
    code: str
    message: str
    hint: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
