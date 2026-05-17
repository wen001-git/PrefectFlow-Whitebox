"""Placeholder validator Python implementation — selftest only."""

from __future__ import annotations

from typing import Any


def run(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"loan_id": r["loan_id"], "principal_x2": r["principal"] * 2}
        for r in rows
    ]
