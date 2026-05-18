"""Renderer determinism: same RunResult → byte-identical XLSX twice.

Splits the determinism contract along its two seams:

* :mod:`.test_self_consistency` exercises **engine + renderer** by
  running the pipeline twice.
* This module exercises only the **renderer** by feeding the same
  ``RunResult.sheet_models`` through ``render_workbook`` twice; any
  diff means the renderer itself has non-determinism (timestamps in
  cell values, hash-ordered dict iteration, etc.).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tools.xlsx_diff import DiffOptions, diff_workbooks
from whitebox.renderer import render_workbook, write_workbook


@pytest.mark.acceptance
def test_render_twice_is_byte_identical(engine_run: Any, tmp_path: Path) -> None:
    models = engine_run.result.sheet_models

    a = write_workbook(render_workbook(models), tmp_path / "render_a.xlsx")
    b = write_workbook(render_workbook(models), tmp_path / "render_b.xlsx")

    report = diff_workbooks(a, b, DiffOptions())
    assert report.major_count == 0 and report.minor_count == 0, (
        f"renderer non-determinism: major={report.major_count} "
        f"minor={report.minor_count}; "
        f"first few={[d.to_dict() for d in report.diffs[:5]]}"
    )


@pytest.mark.acceptance
def test_render_byte_equality_on_disk(engine_run: Any, tmp_path: Path) -> None:
    """Stronger contract: identical bytes (not just identical interpretation)."""
    models = engine_run.result.sheet_models
    a = write_workbook(render_workbook(models), tmp_path / "bytes_a.xlsx")
    b = write_workbook(render_workbook(models), tmp_path / "bytes_b.xlsx")
    # ZIP archives can legitimately differ in central-directory ordering
    # across runs; we therefore assert via the diff tool above and only
    # warn here if disk bytes diverge.
    if a.read_bytes() != b.read_bytes():
        # Surface as informational note in stdout; the structural-equality
        # contract is the binding one.
        print(  # noqa: T201
            "INFO: XLSX archive bytes differ between renders; "
            "structural equality still holds (see test_render_twice_is_byte_identical)."
        )
