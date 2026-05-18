# Integration: Comparison Harness End-to-End Tests

**Round 2 C5 — G2b-LIVE gate**

This directory contains the integration test suite that proves the C1+C3+C4 harness
works end-to-end on trivial examples with **known** differences.

## How to run

```bash
# All integration tests
python -m pytest tests/integration/comparison/ -v

# With timing (verify ≤ 60 s budget)
python -m pytest tests/integration/comparison/ -v --tb=short --durations=10

# Quick smoke check (just this suite)
python -m pytest tests/integration/comparison/test_harness_e2e.py -v
```

## Scenario catalogue

| # | Test name | Setup | Expected verdict | Exit |
|---|-----------|-------|-----------------|------|
| S1 | `test_s1_identical_pristine` | C3 pristine vs C3 pristine (same seed) | PASS | 0 |
| S2 | `test_s2_value_diff` | Baseline vs copy with `Summary!B3 = 9999.99` | MAJOR_DIFFS | 2 |
| S3 | `test_s3_font_only_diff` | Baseline vs copy with bold on `Summary!A2` | MINOR_DIFFS | 1 |
| S4 | `test_s4_missing_sheet` | Baseline (5 sheets) vs copy minus AdvInfo | MAJOR_DIFFS | 2 |
| S5 | `test_s5_extra_sheet` | Baseline (5 sheets) vs copy plus `_EXTRA_SHEET` | MAJOR_DIFFS | 2 |
| S6 | `test_s6_merged_cells_diff` | Baseline vs copy with `Summary!A2:B2` merged | MAJOR_DIFFS | 2 |
| S7 | `test_s7_c3_perturbed_detected` | C3 pristine vs C3 perturbed; all 4 perturbations | MAJOR_DIFFS | 2 |
| S8 | `test_s8_dimension_diff` | Baseline vs copy with extra column on Summary | MAJOR_DIFFS | 2 |
| S9 | `test_s9_float_tolerance_pass` | A=1.0000, B=1.0001 with `--float-tolerance 0.001` | PASS | 0 |
| S10 | `test_s10_ignore_style_suppresses_font` | Font diff + `--ignore-style` | PASS | 0 |
| S11 | `test_s11_dry_run_no_side_effects` | `auto --dry-run` | PASS | 0 |
| +1 | `test_fixture_reproducibility` | Same seed → same fingerprint | N/A | N/A |

## Key assertions per scenario

Each test asserts:
1. **Exit code** matches expected (0/1/2)
2. **`verdict.json`** shape: `verdict`, `summary.major_diff_count`, `summary.minor_diff_count`
3. **Diff categories** in `comparison_report.json`: expected categories present (or absent)
4. **HTML report** exists and is non-empty (> 200 bytes)

S7 additionally asserts each of the 4 documented C3 perturbations is detectable.

## Fixture builders (`_fixtures.py`)

| Builder | Description |
|---------|-------------|
| `build_baseline_workbook(path, seed=42)` | 5-sheet, 5 data rows × 4 cols, deterministic |
| `build_value_diff(path, baseline_path)` | Copy + `Summary!B3 = 9999.99` |
| `build_font_diff(path, baseline_path)` | Copy + `Summary!A2` bold=True |
| `build_missing_sheet(path, baseline_path)` | Copy minus AdvInfo sheet |
| `build_extra_sheet(path, baseline_path)` | Copy plus `_EXTRA_SHEET` |
| `build_merged_cells_diff(path, baseline_path)` | Copy + `Summary!A2:B2` merged |
| `build_dimension_diff(path, baseline_path)` | Copy + 5th column on Summary |
| `workbook_value_fingerprint(path)` | Dict for determinism assertions |

## Examples (representative captured outputs)

Three representative scenario outputs are committed under `examples/`:

- `examples/s1-identical-pristine/` — PASS, zero diffs
- `examples/s2-value-diff/` — MAJOR_DIFFS, single value diff
- `examples/s7-c3-perturbed-detected/` — MAJOR_DIFFS, all 4 C3 perturbations

Each example directory contains:
- `verdict.json`
- `comparison_report.html` (≤ 100 KB)
- `comparison_report.json`
- `README.md` describing what to look at

## How to add a new scenario

1. Add a builder to `_fixtures.py` (if a new XLSX perturbation is needed)
2. Add a `test_sN_<scenario-id>` function in `test_harness_e2e.py`
3. Document the scenario in this README's catalogue table
4. Optionally capture outputs under `examples/<scenario-id>/`

Builder contract:
- Deterministic given seed (call `random.Random(seed)`, not `random.random()`)
- No timestamps or hostname-dependent content inside cells
- Must round-trip through openpyxl save/load without data loss

## What this proves about G2b-LIVE

Passing all 12 tests confirms:

1. **C1 (`xlsx_diff.py`)** detects all major diff categories: value, structure, merged_cells
2. **C1** correctly classifies font diffs as minor (not major)
3. **C1** respects `--float-tolerance` and `--ignore-style` flags
4. **C3 (`run_newsystem_mrc.py`)** generates deterministic XLSX in pristine mode
5. **C4 (`compare_validation.py`)** correctly orchestrates C1+C3 and produces valid verdict.json
6. **All 4 documented C3 perturbations** are detected by the harness

The gate is closed once `test_s7_c3_perturbed_detected` passes, unblocking Stage 2
implementation todos (`stage2-mrc-*-impl`).

## Cross-references

- `plan.md § 9` — G2b-LIVE comparison strategy
- `plan.md § 9.2` — C5 gate requirements
- `docs/stage2/10.0-validation-strategy.{zh,en}.md` — validation strategy document
- `tools/docs/xlsx_diff-help.txt` — C1 CLI help
- `tools/docs/run_legacy_mrc.md` — C2 documentation
- `tools/docs/run_newsystem_mrc.md` — C3 documentation
- `tools/docs/compare_validation.md` — C4 documentation
