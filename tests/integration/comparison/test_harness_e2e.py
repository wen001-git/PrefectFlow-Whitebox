"""
tests/integration/comparison/test_harness_e2e.py
=================================================
Round 2 C5 — End-to-end harness validation (THE GATE).

This is the integration suite that exercises C1 + C3 + C4 together in
realistic operator workflows.  It proves the harness works on hand-built
trivial examples with **known** differences, acting as a regression gate
for any future change to C1-C4.

Cross-refs:
    plan.md § 9.2 (G2b-LIVE gate)
    docs/stage2/10.0-validation-strategy.{zh,en}.md
    tools/xlsx_diff.py        (C1)
    tools/run_newsystem_mrc.py (C3)
    tools/compare_validation.py (C4)

Runtime budget: full suite ≤ 60 s.

Scenario catalogue
------------------
S1  identical-pristine         — C3 pristine vs C3 pristine  → PASS exit 0
S2  value-diff                 — single cell value change     → MAJOR_DIFFS exit 2
S3  font-only-diff             — bold flag on one cell        → MINOR_DIFFS exit 1
S4  missing-sheet              — A has 5 sheets, B has 4      → MAJOR_DIFFS exit 2
S5  extra-sheet                — A has 5 sheets, B has 6      → MAJOR_DIFFS exit 2
S6  merged-cells-diff          — merged range set differs     → MAJOR_DIFFS exit 2
S7  c3-perturbed-detected      — C3 pristine vs C3 perturbed  → MAJOR_DIFFS exit 2;
                                   all 4 documented C3 perturbations detected
S8  dimension-diff             — A is N×4, B is N×5 extra col → MAJOR_DIFFS exit 2
S9  float-tolerance-pass       — A=1.0, B=1.0001, tol=0.001  → PASS exit 0
S10 ignore-style-suppresses-font — font diff + --ignore-style → PASS exit 0
S11 dry-run-no-side-effects    — auto --dry-run               → exit 0, no artifacts
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import openpyxl
import pytest
from openpyxl.styles import Font

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
_REPO_ROOT = _HERE.parent.parent.parent
_TOOLS_DIR = _REPO_ROOT / "tools"
_COMPARE_VALIDATION = _TOOLS_DIR / "compare_validation.py"
_RUN_NEWSYSTEM = _TOOLS_DIR / "run_newsystem_mrc.py"

# ---------------------------------------------------------------------------
# Guard: skip entire module if compare_validation.py or openpyxl unavailable
# ---------------------------------------------------------------------------

# (no module-level pytestmark needed)


def _skip_if_unavailable() -> None:
    """Raise pytest.skip if key dependencies are missing."""
    if not _COMPARE_VALIDATION.exists():
        pytest.skip("compare_validation.py not found — C4 not installed")
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        pytest.skip("openpyxl not available")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from tests.integration.comparison._fixtures import (  # noqa: E402
    build_baseline_workbook,
    build_dimension_diff,
    build_extra_sheet,
    build_font_diff,
    build_merged_cells_diff,
    build_missing_sheet,
    build_value_diff,
    workbook_value_fingerprint,
)


def _run_compare(
    legacy: Path,
    new_xlsx: Path,
    report_dir: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke compare_validation.py compare subcommand via subprocess."""
    cmd: list[str] = [
        sys.executable, str(_COMPARE_VALIDATION),
        "compare",
        "--legacy-xlsx", str(legacy),
        "--new-xlsx", str(new_xlsx),
        "--report-dir", str(report_dir),
        "--quiet",
    ]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


def _run_newsystem(
    out_dir: Path,
    mode: str = "pristine",
    seed: int = 42,
) -> subprocess.CompletedProcess[str]:
    """Invoke run_newsystem_mrc.py via subprocess."""
    cmd: list[str] = [
        sys.executable, str(_RUN_NEWSYSTEM),
        "--servicer", "mrc",
        "--remit-date", "2026-04-30",
        "--out-dir", str(out_dir),
        "--mode", mode,
        "--seed", str(seed),
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def _load_verdict(report_dir: Path) -> dict[str, Any]:
    verdict_path = report_dir / "verdict.json"
    assert verdict_path.exists(), f"verdict.json missing from {report_dir}"
    return json.loads(verdict_path.read_text(encoding="utf-8"))


def _load_comparison_report(report_dir: Path) -> dict[str, Any]:
    rpt_path = report_dir / "comparison_report.json"
    assert rpt_path.exists(), f"comparison_report.json missing from {report_dir}"
    return json.loads(rpt_path.read_text(encoding="utf-8"))


def _diff_categories(comparison_report: dict[str, Any]) -> set[str]:
    return {d["category"] for d in comparison_report.get("diffs", [])}


def _assert_html_nonempty(report_dir: Path) -> None:
    html = report_dir / "comparison_report.html"
    assert html.exists(), f"comparison_report.html missing from {report_dir}"
    assert html.stat().st_size > 200, f"comparison_report.html is suspiciously small ({html.stat().st_size} bytes)"


# ---------------------------------------------------------------------------
# S1 — identical-pristine
# ---------------------------------------------------------------------------


def test_s1_identical_pristine(tmp_path: Path) -> None:
    """S1: C3 pristine vs C3 pristine (same seed) must be cell-identical → PASS exit 0.

    Cross-ref: plan.md § 9.2 · ch 1.6 baseline contract.
    Exercises: harness self-test pathway.
    """
    _skip_if_unavailable()

    legacy_dir = tmp_path / "legacy"
    new_dir = tmp_path / "new"
    report_dir = tmp_path / "report"

    # Generate two pristine XLSXs with same seed
    r1 = _run_newsystem(legacy_dir, mode="pristine", seed=42)
    assert r1.returncode == 0, f"C3 legacy run failed: {r1.stderr}"
    r2 = _run_newsystem(new_dir, mode="pristine", seed=42)
    assert r2.returncode == 0, f"C3 new run failed: {r2.stderr}"

    legacy_xlsx = legacy_dir / "validation_report.xlsx"
    new_xlsx = new_dir / "validation_report.xlsx"
    assert legacy_xlsx.exists()
    assert new_xlsx.exists()

    result = _run_compare(legacy_xlsx, new_xlsx, report_dir)

    # Exit 0 = identical
    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "PASS"
    assert verdict["exit_code"] == 0
    assert verdict["summary"]["identical"] is True
    assert verdict["summary"]["major_diff_count"] == 0
    assert verdict["summary"]["minor_diff_count"] == 0

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S2 — value-diff
# ---------------------------------------------------------------------------


def test_s2_value_diff(tmp_path: Path) -> None:
    """S2: Single cell value change → MAJOR_DIFFS exit 2, category 'value'.

    Cross-ref: plan.md § 9.2 · ch 1.6 § value equivalence.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_value_diff(modified, baseline)

    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "value" in cats, f"Expected 'value' category in diff categories; got {cats}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S3 — font-only-diff
# ---------------------------------------------------------------------------


def test_s3_font_only_diff(tmp_path: Path) -> None:
    """S3: Bold flag changed on one cell, no value change → MINOR_DIFFS exit 1.

    Must have category 'font' and NO 'value' diffs.
    Cross-ref: plan.md § 9.2 · C1 minor-diff semantics.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_font_diff(modified, baseline)

    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 1, (
        f"Expected exit 1 (MINOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MINOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] == 0
    assert verdict["summary"]["minor_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "font" in cats, f"Expected 'font' category; got {cats}"
    assert "value" not in cats, (
        f"Unexpected 'value' category present — font-only diff should not affect values; cats={cats}"
    )

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S4 — missing-sheet
# ---------------------------------------------------------------------------


def test_s4_missing_sheet(tmp_path: Path) -> None:
    """S4: Legacy has 5 sheets, new has 4 (AdvInfo removed) → MAJOR_DIFFS exit 2.

    Must include category 'structure' diff for the missing sheet.
    Cross-ref: plan.md § 9.2 · C1 sheet-missing detection.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_missing_sheet(modified, baseline)

    # legacy = baseline (5 sheets), new = modified (4 sheets)
    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "structure" in cats, f"Expected 'structure' category; got {cats}"

    # Specifically: AdvInfo sheet should be flagged as missing-in-new
    struct_diffs = [d for d in rpt["diffs"] if d["category"] == "structure"]
    assert any(
        d.get("sheet") == "AdvInfo" or "AdvInfo" in str(d.get("legacy", "")) or "AdvInfo" in str(d.get("new", ""))
        for d in struct_diffs
    ), f"AdvInfo not mentioned in structure diffs: {struct_diffs}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S5 — extra-sheet
# ---------------------------------------------------------------------------


def test_s5_extra_sheet(tmp_path: Path) -> None:
    """S5: Legacy has 5 sheets, new has 6 (extra _EXTRA_SHEET) → MAJOR_DIFFS exit 2.

    Must include category 'structure' diff for the extra sheet.
    Cross-ref: plan.md § 9.2 · C1 sheet-extra detection.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_extra_sheet(modified, baseline)

    # legacy = baseline (5 sheets), new = modified (6 sheets)
    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "structure" in cats, f"Expected 'structure' category; got {cats}"

    # _EXTRA_SHEET should be flagged as present only in new
    struct_diffs = [d for d in rpt["diffs"] if d["category"] == "structure"]
    assert any(
        d.get("sheet") == "_EXTRA_SHEET" or "_EXTRA_SHEET" in str(d.get("new", ""))
        for d in struct_diffs
    ), f"_EXTRA_SHEET not mentioned in structure diffs: {struct_diffs}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S6 — merged-cells-diff
# ---------------------------------------------------------------------------


def test_s6_merged_cells_diff(tmp_path: Path) -> None:
    """S6: One side has merged range A2:B2, other does not → MAJOR_DIFFS exit 2.

    Must include category 'merged_cells'.
    Cross-ref: plan.md § 9.2 · C1 merged-cell detection.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_merged_cells_diff(modified, baseline)

    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "merged_cells" in cats, f"Expected 'merged_cells' category; got {cats}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S7 — c3-perturbed-detected (THE KEY GATE TEST)
# ---------------------------------------------------------------------------


def _detect_perturbation(pert_id: str, diffs: list[dict[str, Any]]) -> bool:
    """Return True if the given C3 perturbation is detectable in the diff list."""
    if pert_id == "value_diff":
        return any(d["category"] == "value" for d in diffs)
    if pert_id == "font_diff":
        return any(d["category"] == "font" for d in diffs)
    if pert_id == "missing_row":
        # Missing row causes dimension diff (structure) on MRC_ServiceFee_Check
        # OR value diffs in the removed row (cells present in legacy but absent in new)
        return any(
            d["category"] in ("structure", "value")
            and d.get("sheet") == "MRC_ServiceFee_Check"
            for d in diffs
        )
    if pert_id == "extra_sheet":
        # Extra sheet causes structure diff; the workbook-level sheet-list diff
        # is on sheet="(workbook)" and the per-sheet diff is on "_PERTURBATION_EXTRA"
        return any(
            d["category"] == "structure"
            and (
                d.get("sheet") == "_PERTURBATION_EXTRA"
                or "_PERTURBATION_EXTRA" in str(d.get("legacy", ""))
                or "_PERTURBATION_EXTRA" in str(d.get("new", ""))
            )
            for d in diffs
        )
    return False


def test_s7_c3_perturbed_detected(tmp_path: Path) -> None:
    """S7: C3 pristine vs C3 perturbed → MAJOR_DIFFS; all 4 documented perturbations detected.

    Exercises the full end-to-end auto path through C3 + C4:
      1. Shell out to run_newsystem_mrc.py --mode pristine (acting as "legacy" side)
      2. Shell out to run_newsystem_mrc.py --mode perturbed
      3. Compare via compare_validation.py compare
      4. Read perturbations.json to learn expected perturbations
      5. Assert each documented perturbation is detectable in the diff output

    If a documented perturbation is NOT detected, the test FAILS with a clear message
    identifying the slipped-through perturbation (indicating a C1 or C3 bug).

    Cross-ref: plan.md § 9.2 · docs/stage2/10.0-validation-strategy.en.md § harness-gate.
    """
    _skip_if_unavailable()
    if not _RUN_NEWSYSTEM.exists():
        pytest.skip("run_newsystem_mrc.py not found — C3 not installed")

    legacy_dir = tmp_path / "legacy"
    new_dir = tmp_path / "new"
    report_dir = tmp_path / "report"

    # Step 1: generate pristine XLSX (acts as legacy baseline)
    r_pristine = _run_newsystem(legacy_dir, mode="pristine", seed=42)
    assert r_pristine.returncode == 0, f"C3 pristine run failed:\n{r_pristine.stderr}"
    legacy_xlsx = legacy_dir / "validation_report.xlsx"
    assert legacy_xlsx.exists(), "C3 pristine did not produce validation_report.xlsx"

    # Step 2: generate perturbed XLSX
    r_perturbed = _run_newsystem(new_dir, mode="perturbed", seed=42)
    assert r_perturbed.returncode == 0, f"C3 perturbed run failed:\n{r_perturbed.stderr}"
    new_xlsx = new_dir / "validation_report.xlsx"
    pert_json = new_dir / "perturbations.json"
    assert new_xlsx.exists(), "C3 perturbed did not produce validation_report.xlsx"
    assert pert_json.exists(), "C3 perturbed did not produce perturbations.json"

    # Step 3: compare
    result = _run_compare(
        legacy_xlsx, new_xlsx, report_dir,
        extra_args=["--new-mode", "perturbed"],
    )
    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) for perturbed vs pristine "
        f"but got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 2, (
        f"Expected major_diff_count >= 2; got {verdict['summary']['major_diff_count']}. "
        "At minimum value_diff + extra_sheet must register as major diffs."
    )

    # Step 4: load documented perturbations
    perturbations: list[dict[str, Any]] = json.loads(pert_json.read_text(encoding="utf-8"))
    pert_ids = [p["id"] for p in perturbations if isinstance(p, dict) and "id" in p]
    assert len(pert_ids) >= 4, f"Expected >= 4 documented perturbations; got {pert_ids}"

    # Step 5: assert each perturbation is detectable
    rpt = _load_comparison_report(report_dir)
    diffs = rpt.get("diffs", [])
    cats = _diff_categories(rpt)

    # Broad category assertions
    assert "value" in cats, (
        "Category 'value' absent from diffs — value_diff perturbation slipped through. "
        "This indicates a bug in C1 (xlsx_diff.py) or C3 (run_newsystem_mrc.py)."
    )
    assert "structure" in cats, (
        "Category 'structure' absent from diffs — extra_sheet or missing_row perturbation "
        "slipped through. This indicates a bug in C1 or C3."
    )

    # Per-perturbation assertions
    slipped_through: list[str] = []
    for pert_id in pert_ids:
        if not _detect_perturbation(pert_id, diffs):
            slipped_through.append(pert_id)

    assert not slipped_through, (
        f"The following documented C3 perturbations were NOT detected by the harness: "
        f"{slipped_through}. "
        "This is a bug in C1 (xlsx_diff.py) or C3 (run_newsystem_mrc.py) that needs "
        "Round 3 follow-up. Diff categories found: " + str(cats)
    )

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S8 — dimension-diff
# ---------------------------------------------------------------------------


def test_s8_dimension_diff(tmp_path: Path) -> None:
    """S8: Legacy has N×4 sheet, new has N×5 (extra column E) → MAJOR_DIFFS exit 2.

    Must include category 'structure' for the dimension mismatch.
    Cross-ref: plan.md § 9.2 · C1 dimension detection.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_dimension_diff(modified, baseline)

    result = _run_compare(baseline, modified, report_dir)

    assert result.returncode == 2, (
        f"Expected exit 2 (MAJOR_DIFFS) but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "MAJOR_DIFFS"
    assert verdict["summary"]["major_diff_count"] >= 1

    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "structure" in cats, (
        f"Expected 'structure' category for dimension diff; got {cats}"
    )

    # Specifically: Summary sheet should have a dimension diff
    struct_diffs = [d for d in rpt["diffs"] if d["category"] == "structure"]
    assert any(
        d.get("sheet") == "Summary" for d in struct_diffs
    ), f"Summary sheet not in structure diffs: {struct_diffs}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S9 — float-tolerance-pass
# ---------------------------------------------------------------------------


def test_s9_float_tolerance_pass(tmp_path: Path) -> None:
    """S9: A=1.0000, B=1.0001 within --float-tolerance 0.001 → PASS exit 0.

    Verifies that C1's tolerance mechanism suppresses near-equal float diffs.
    Cross-ref: plan.md § 9.2 · tools/docs/xlsx_diff-help.txt --float-tolerance.
    """
    _skip_if_unavailable()

    # Build two single-sheet workbooks with a known tiny float diff
    wb_a = openpyxl.Workbook()
    ws_a = wb_a.active
    assert ws_a is not None
    ws_a["A1"] = 1.0000

    wb_b = openpyxl.Workbook()
    ws_b = wb_b.active
    assert ws_b is not None
    ws_b["A1"] = 1.0001  # diff = 0.0001, within tolerance 0.001

    a_path = tmp_path / "a.xlsx"
    b_path = tmp_path / "b.xlsx"
    wb_a.save(str(a_path))
    wb_b.save(str(b_path))

    report_dir = tmp_path / "report"
    result = _run_compare(a_path, b_path, report_dir, extra_args=["--float-tolerance", "0.001"])

    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) with float tolerance 0.001 but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "PASS"
    assert verdict["summary"]["major_diff_count"] == 0

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S10 — ignore-style-suppresses-font
# ---------------------------------------------------------------------------


def test_s10_ignore_style_suppresses_font(tmp_path: Path) -> None:
    """S10: Font diff with --ignore-style → PASS exit 0.

    Verifies that --ignore-style suppresses all font/fill/border/alignment diffs.
    Compare with S3 (same fixture, no flag → MINOR_DIFFS).
    Cross-ref: plan.md § 9.2 · C1 --ignore-style flag.
    """
    _skip_if_unavailable()

    baseline = tmp_path / "baseline.xlsx"
    modified = tmp_path / "modified.xlsx"
    report_dir = tmp_path / "report"

    build_baseline_workbook(baseline, seed=42)
    build_font_diff(modified, baseline)

    result = _run_compare(baseline, modified, report_dir, extra_args=["--ignore-style"])

    assert result.returncode == 0, (
        f"Expected exit 0 (PASS) with --ignore-style but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    verdict = _load_verdict(report_dir)
    assert verdict["verdict"] == "PASS"
    # With --ignore-style, no font diffs should appear
    rpt = _load_comparison_report(report_dir)
    cats = _diff_categories(rpt)
    assert "font" not in cats, f"Font category appeared despite --ignore-style; cats={cats}"

    _assert_html_nonempty(report_dir)


# ---------------------------------------------------------------------------
# S11 — dry-run-no-side-effects
# ---------------------------------------------------------------------------


def test_s11_dry_run_no_side_effects(tmp_path: Path) -> None:
    """S11: auto --dry-run → exit 0; no XLSX, no verdict.json, no artifacts created.

    Verifies the --dry-run flag is truly side-effect-free for the report directory.
    Cross-ref: plan.md § 9.2 · compare_validation.py auto --dry-run.
    """
    _skip_if_unavailable()

    report_dir = tmp_path / "dry_run_report"
    # report_dir must NOT be pre-created; auto --dry-run should not create it

    cmd = [
        sys.executable, str(_COMPARE_VALIDATION),
        "auto",
        "--servicer", "mrc",
        "--remit-date", "2026-04-30",
        "--new-mode", "pristine",
        "--report-dir", str(report_dir),
        "--dry-run",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"Expected exit 0 from dry-run but got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Dry-run must not create any output files
    assert not (report_dir / "verdict.json").exists(), (
        "verdict.json was created despite --dry-run"
    )
    assert not (report_dir / "comparison_report.xlsx").exists(), (
        "comparison_report.xlsx was created despite --dry-run"
    )
    assert not (report_dir / "comparison_report.html").exists(), (
        "comparison_report.html was created despite --dry-run"
    )
    assert not (report_dir / "validation_report.xlsx").exists(), (
        "validation_report.xlsx was created despite --dry-run"
    )

    # Dry-run should print the plan
    assert "DRY-RUN" in result.stdout or "dry" in result.stdout.lower(), (
        f"Expected dry-run plan in stdout but got: {result.stdout[:500]}"
    )


# ---------------------------------------------------------------------------
# Bonus: fixture reproducibility test
# ---------------------------------------------------------------------------


def test_fixture_reproducibility(tmp_path: Path) -> None:
    """Baseline workbook built with the same seed must produce identical fingerprints.

    Verifies builder determinism: two independent builds from seed=42 are cell-equal.
    Cross-ref: plan.md § 9.2 deliverable #2 (deterministic fixtures).
    """
    p1 = tmp_path / "wb1.xlsx"
    p2 = tmp_path / "wb2.xlsx"
    build_baseline_workbook(p1, seed=42)
    build_baseline_workbook(p2, seed=42)

    fp1 = workbook_value_fingerprint(p1)
    fp2 = workbook_value_fingerprint(p2)
    assert fp1 == fp2, "Same seed produced different workbooks — builder is not deterministic"

    # Different seed must differ
    p3 = tmp_path / "wb3.xlsx"
    build_baseline_workbook(p3, seed=999)
    fp3 = workbook_value_fingerprint(p3)
    assert fp1 != fp3, "Different seeds should produce different workbooks"
