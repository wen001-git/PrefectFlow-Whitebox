"""Self-consistency: two independent engine runs must be cell-identical.

Determinism is the *floor* of the acceptance contract: if two runs of
the engine, end-to-end, against the same source produce different
XLSX bytes, the engine has a non-determinism bug and **all other
comparisons are invalid** (you cannot diff against a baseline if
"the new system" is a moving target).

This test always runs, regardless of which legacy/baseline mode is
active. A failure here is a real bug, not an environment skip.
"""

from __future__ import annotations

from typing import Any

import pytest

from tools.xlsx_diff import DiffOptions, diff_workbooks


@pytest.mark.acceptance
def test_two_runs_are_cell_identical(engine_run_factory: Any) -> None:
    a = engine_run_factory("self_a")
    b = engine_run_factory("self_b")

    report = diff_workbooks(a.xlsx_path, b.xlsx_path, DiffOptions())

    assert report.major_count == 0, (
        "engine is non-deterministic (MAJOR diffs between two runs): "
        f"{report.major_count}; first few={[d.to_dict() for d in report.diffs[:5]]}"
    )
    assert report.minor_count == 0, (
        "engine is non-deterministic (MINOR diffs between two runs): "
        f"{report.minor_count}; first few={[d.to_dict() for d in report.diffs[:5]]}"
    )


@pytest.mark.acceptance
def test_run_id_is_deterministic(engine_run_factory: Any) -> None:
    """Same (servicer, remit_date, source) → same run_id."""
    a = engine_run_factory("rid_a")
    b = engine_run_factory("rid_b")
    assert a.result.run_id == b.result.run_id
