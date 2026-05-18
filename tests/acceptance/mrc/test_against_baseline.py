"""Diff one engine run against the captured legacy baseline XLSX.

This test is the "long-term ideal" arm of the acceptance gate
(`docs/stage2/10.0-validation-strategy.en.md` §2): once an operator
has captured a known-good legacy run into
``baselines/mrc/<date>/validation_report.xlsx`` (see
``CAPTURE_INSTRUCTIONS.md`` in that directory), every PR replays the
engine and diffs against that frozen baseline.

If the baseline is absent the test ENV-SKIPs cleanly — that is NOT
a failure, just a documented environment limitation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tools.xlsx_diff import DiffOptions, diff_workbooks


def _is_allowlisted(diff: Any, allowlist: list[dict[str, Any]]) -> bool:
    for entry in allowlist:
        if (
            entry.get("sheet") == diff.sheet
            and entry.get("cell_ref") == f"{diff.col}{diff.row}"
            and entry.get("dimension") == diff.category
        ):
            return True
    return False


@pytest.mark.acceptance
@pytest.mark.needs_baseline
def test_engine_matches_baseline_xlsx(
    engine_run: Any,
    baseline_xlsx: Path,
    allowlist: list[dict[str, Any]],
) -> None:
    report = diff_workbooks(baseline_xlsx, engine_run.xlsx_path, DiffOptions())

    # MAJOR diffs are never allowlistable — they always FAIL the gate.
    assert report.major_count == 0, (
        f"engine output diverges from baseline on {report.major_count} MAJOR cells; "
        f"first few={[d.to_dict() for d in report.diffs if d.severity == 'major'][:5]}"
    )

    # MINOR diffs only pass if every one of them is documented in the
    # allowlist (sheet + cell_ref + dimension match).
    undocumented = [
        d
        for d in report.diffs
        if d.severity == "minor" and not _is_allowlisted(d, allowlist)
    ]
    assert not undocumented, (
        f"{len(undocumented)} undocumented MINOR diff(s) vs baseline; "
        f"add to acceptance_minor_diffs_allowlist.json with ADR_ref: "
        f"{[d.to_dict() for d in undocumented[:5]]}"
    )
