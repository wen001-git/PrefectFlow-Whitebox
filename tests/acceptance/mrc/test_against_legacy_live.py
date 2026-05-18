"""Live legacy-vs-new diff (G2b-LIVE arm of the acceptance gate).

When credentials are available, this test invokes both the real
legacy ``flow/remit_validation`` MRC entrypoint and the new engine,
within the same window, and diffs the two XLSX files. The window
matters: per ``docs/stage2/10.0-validation-strategy.en.md`` §6.1,
Redshift state can drift between days, so the two runs must be from
the same instant to be comparable.

ENV-SKIPs cleanly when ``ACCEPTANCE_LEGACY_LIVE`` is not set or
Vault credentials are absent; that is **not** a test failure.
"""

from __future__ import annotations

from typing import Any

import pytest

from tools.xlsx_diff import DiffOptions, diff_workbooks


@pytest.mark.acceptance
@pytest.mark.needs_legacy_live
def test_engine_matches_live_legacy(
    engine_run: Any,
    legacy_run: Any,
    allowlist: list[dict[str, Any]],
) -> None:
    report = diff_workbooks(legacy_run.xlsx_path, engine_run.xlsx_path, DiffOptions())

    assert report.major_count == 0, (
        f"engine output diverges from live legacy on {report.major_count} MAJOR cells; "
        f"first few={[d.to_dict() for d in report.diffs if d.severity == 'major'][:5]}"
    )

    undocumented = [
        d
        for d in report.diffs
        if d.severity == "minor"
        and not any(
            e.get("sheet") == d.sheet
            and e.get("cell_ref") == f"{d.col}{d.row}"
            and e.get("dimension") == d.category
            for e in allowlist
        )
    ]
    assert not undocumented, (
        f"{len(undocumented)} undocumented MINOR diff(s) vs live legacy; "
        f"first few={[d.to_dict() for d in undocumented[:5]]}"
    )
