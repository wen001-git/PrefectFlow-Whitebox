"""Smoke + branch tests for ``tools/acceptance_gate.py``.

These tests exercise the CLI tool itself (not the pytest acceptance
suite — that lives under :mod:`tests.acceptance.mrc`). They are kept
under ``tests/tools/`` like the other tool tests so the acceptance
suite can stay focused on engine-output behaviour.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

from tools.acceptance_gate import (
    EXIT_ERROR,
    EXIT_MAJOR,
    EXIT_PASS,
    VERDICT_MAJOR,
    VERDICT_PASS,
    VERDICT_SKIPPED,
    _aggregate_verdict,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _invoke(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(REPO_ROOT / "tools" / "acceptance_gate.py"), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_smoke_skip_mode_passes(tmp_path: Path) -> None:
    out = tmp_path / "out"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--legacy-mode",
            "skip",
            "--output",
            str(out),
        ]
    )
    assert proc.returncode == EXIT_PASS, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    verdict = json.loads((out / "acceptance_verdict.json").read_text(encoding="utf-8"))
    assert verdict["verdict"] == VERDICT_PASS
    assert verdict["exit_code"] == EXIT_PASS
    assert verdict["components"]["self_consistency"]["status"] == VERDICT_PASS
    assert verdict["components"]["baseline"]["status"] == VERDICT_SKIPPED
    assert verdict["components"]["legacy_live"]["status"] == VERDICT_SKIPPED
    # Required artifacts must all exist.
    for name in (
        "engine_output.xlsx",
        "engine_output_rerun.xlsx",
        "self_diff.json",
        "acceptance_verdict.json",
        "acceptance_report.md",
    ):
        assert (out / name).exists(), f"missing artifact: {name}"


def test_cli_skip_mode_with_missing_baseline_path(tmp_path: Path) -> None:
    """A baseline path that does not exist must SKIP cleanly, not error."""
    out = tmp_path / "out"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--baseline",
            str(tmp_path / "no_such_baseline.xlsx"),
            "--legacy-mode",
            "skip",
            "--output",
            str(out),
        ]
    )
    assert proc.returncode == EXIT_PASS
    verdict = json.loads((out / "acceptance_verdict.json").read_text(encoding="utf-8"))
    assert verdict["components"]["baseline"]["status"] == VERDICT_SKIPPED
    assert "not found" in verdict["components"]["baseline"]["reason"]


def test_cli_baseline_present_and_identical_passes(tmp_path: Path) -> None:
    """When baseline == engine output, baseline component is PASS."""
    # First, produce an engine output to use as the "baseline".
    seed_out = tmp_path / "seed"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--legacy-mode",
            "skip",
            "--output",
            str(seed_out),
        ]
    )
    assert proc.returncode == EXIT_PASS, f"seed run failed: {proc.stderr}"
    baseline = tmp_path / "baseline.xlsx"
    baseline.write_bytes((seed_out / "engine_output.xlsx").read_bytes())

    # Now run again with that baseline.
    out = tmp_path / "out"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--baseline",
            str(baseline),
            "--legacy-mode",
            "skip",
            "--output",
            str(out),
        ]
    )
    assert proc.returncode == EXIT_PASS, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    verdict = json.loads((out / "acceptance_verdict.json").read_text(encoding="utf-8"))
    assert verdict["verdict"] == VERDICT_PASS
    assert verdict["components"]["baseline"]["status"] == VERDICT_PASS
    assert verdict["components"]["baseline"]["major"] == 0
    assert verdict["components"]["baseline"]["minor"] == 0
    assert (out / "baseline_diff.json").exists()
    assert (out / "baseline_diff.html").exists()


def test_cli_baseline_with_major_diff_fails(tmp_path: Path) -> None:
    """A baseline that differs on a cell VALUE must produce MAJOR_DIFFS."""
    # Seed an engine output, then mutate one cell to create a value diff.
    seed_out = tmp_path / "seed"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--legacy-mode",
            "skip",
            "--output",
            str(seed_out),
        ]
    )
    assert proc.returncode == EXIT_PASS
    baseline = tmp_path / "baseline_mutated.xlsx"
    baseline.write_bytes((seed_out / "engine_output.xlsx").read_bytes())

    wb = openpyxl.load_workbook(baseline)
    ws = wb["MRC_Summary_check"]
    ws.cell(row=1, column=1).value = "MUTATED HEADER"
    wb.save(baseline)

    out = tmp_path / "out"
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--baseline",
            str(baseline),
            "--legacy-mode",
            "skip",
            "--output",
            str(out),
        ]
    )
    assert proc.returncode == EXIT_MAJOR
    verdict = json.loads((out / "acceptance_verdict.json").read_text(encoding="utf-8"))
    assert verdict["verdict"] == VERDICT_MAJOR
    assert verdict["components"]["baseline"]["status"] == VERDICT_MAJOR
    assert verdict["components"]["baseline"]["major"] >= 1


def test_aggregate_verdict_self_diff_promotes_to_major() -> None:
    """Any self_consistency diff must escalate to MAJOR regardless of others."""
    components = {
        "self_consistency": {"status": "MINOR_DIFFS", "major": 0, "minor": 1},
        "baseline": {"status": "PASS"},
        "legacy_live": {"status": "SKIPPED"},
    }
    verdict, exit_code = _aggregate_verdict(components)
    assert verdict == VERDICT_MAJOR
    assert exit_code == EXIT_MAJOR


def test_aggregate_verdict_all_pass() -> None:
    components = {
        "self_consistency": {"status": "PASS"},
        "baseline": {"status": "PASS"},
        "legacy_live": {"status": "SKIPPED"},
    }
    verdict, exit_code = _aggregate_verdict(components)
    assert verdict == VERDICT_PASS
    assert exit_code == EXIT_PASS


def test_aggregate_verdict_error_in_self_short_circuits() -> None:
    components = {
        "self_consistency": {"status": "ERROR"},
        "baseline": {"status": "PASS"},
        "legacy_live": {"status": "SKIPPED"},
    }
    verdict, exit_code = _aggregate_verdict(components)
    assert verdict == "ERROR"
    assert exit_code == EXIT_ERROR


def test_cli_rejects_bad_legacy_mode(tmp_path: Path) -> None:
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--legacy-mode",
            "bogus",
            "--output",
            str(tmp_path / "out"),
        ]
    )
    assert proc.returncode != 0
    assert "invalid choice" in proc.stderr.lower() or "usage:" in proc.stderr.lower()


def test_cli_invalid_allowlist_returns_error(tmp_path: Path) -> None:
    bad = tmp_path / "allowlist.json"
    bad.write_text("{not valid json", encoding="utf-8")
    proc = _invoke(
        [
            "--servicer",
            "MRC",
            "--remit-date",
            "2026-04-30",
            "--legacy-mode",
            "skip",
            "--output",
            str(tmp_path / "out"),
            "--allowlist",
            str(bad),
        ]
    )
    assert proc.returncode == EXIT_ERROR


@pytest.mark.parametrize(
    "components, expected_verdict",
    [
        (
            {
                "self_consistency": {"status": "PASS"},
                "baseline": {"status": "MINOR_DIFFS"},
                "legacy_live": {"status": "SKIPPED"},
            },
            "MINOR_DIFFS",
        ),
        (
            {
                "self_consistency": {"status": "PASS"},
                "baseline": {"status": "MAJOR_DIFFS"},
                "legacy_live": {"status": "PASS"},
            },
            "MAJOR_DIFFS",
        ),
        (
            {
                "self_consistency": {"status": "SKIPPED"},
                "baseline": {"status": "SKIPPED"},
                "legacy_live": {"status": "SKIPPED"},
            },
            "SKIPPED",
        ),
    ],
)
def test_aggregate_verdict_table(
    components: dict[str, dict[str, str]], expected_verdict: str
) -> None:
    verdict, _ = _aggregate_verdict(components)
    assert verdict == expected_verdict
