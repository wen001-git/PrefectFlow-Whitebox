"""Meta-test: aggregates the three modes into a single PASS/FAIL gate.

This is the test-tier sibling of ``tools/acceptance_gate.py``. It
ensures that:

* The allowlist file is present and well-formed, AND every entry has
  the required keys (``sheet``, ``cell_ref``, ``dimension``,
  ``justification``, ``ADR_ref``).
* The allowlist is **only consulted for MINOR diffs** — a MAJOR diff
  is always a hard FAIL regardless of allowlist content.
* Self-consistency is green (the floor).

If a baseline / legacy live run is available in this environment, the
companion test modules will assert against them; this meta-test does
not re-run those comparisons but checks the surrounding policy.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.xlsx_diff import DiffOptions, diff_workbooks

REQUIRED_ALLOWLIST_KEYS = ("sheet", "cell_ref", "dimension", "justification", "ADR_ref")

ALLOWLIST_PATH = (
    Path(__file__).resolve().parent / "acceptance_minor_diffs_allowlist.json"
)


@pytest.mark.acceptance
def test_allowlist_file_exists_and_is_json_array() -> None:
    assert ALLOWLIST_PATH.exists(), (
        f"acceptance_minor_diffs_allowlist.json missing at {ALLOWLIST_PATH}"
    )
    raw = ALLOWLIST_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return  # empty file is treated as []
    data = json.loads(raw)
    assert isinstance(data, list), "allowlist must be a JSON array"


@pytest.mark.acceptance
def test_allowlist_entries_have_required_keys(
    allowlist: list[dict[str, Any]],
) -> None:
    for i, entry in enumerate(allowlist):
        for key in REQUIRED_ALLOWLIST_KEYS:
            assert key in entry, (
                f"allowlist entry #{i} missing required key {key!r}: {entry!r}"
            )
            assert entry[key], (
                f"allowlist entry #{i} has empty {key!r}: {entry!r}"
            )
        assert entry["dimension"] not in {
            "value",
            "formula",
            "merged_cells",
            "structure",
        }, (
            f"allowlist entry #{i} attempts to allowlist a MAJOR dimension "
            f"{entry['dimension']!r}; MAJOR diffs are NEVER allowlistable "
            f"(see docs/stage2/12.0-acceptance-gate.en.md)"
        )


@pytest.mark.acceptance
def test_acceptance_gate_floor_self_consistency_passes(
    engine_run_factory: Any,
) -> None:
    """The floor: two engine runs must be cell-identical. Hard FAIL otherwise."""
    a = engine_run_factory("gate_a")
    b = engine_run_factory("gate_b")
    report = diff_workbooks(a.xlsx_path, b.xlsx_path, DiffOptions())
    assert report.major_count == 0 and report.minor_count == 0, (
        "ACCEPTANCE GATE FLOOR VIOLATION: self-consistency failed. "
        "Engine is non-deterministic; fix before evaluating any other tier. "
        f"major={report.major_count} minor={report.minor_count}"
    )
