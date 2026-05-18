# S7 — c3-perturbed-detected: MAJOR_DIFFS

**Scenario:** C3 pristine (acting as legacy) vs C3 perturbed — all 4 documented perturbations detected

**Expected verdict:** `MAJOR_DIFFS` — exit code 2, `major_diff_count >= 2`

**Files:**
- `verdict.json` — `verdict: "MAJOR_DIFFS"`, `summary.major_diff_count >= 2`
- `comparison_report.json` — categories include `value`, `structure`, `font`
- `comparison_report.html` — HTML report detailing all detected differences
- `perturbations.json` — 4 documented injected perturbations from C3

## The 4 documented perturbations

See `perturbations.json` for the exact C3 specification:

| id | Location | Change |
|----|----------|--------|
| `value_diff` | `MRC_General_Check` row 2 `rate` | 0.04 → 0.05 |
| `font_diff` | `MRC_Advance_Check` cell A2 | bold=False → bold=True |
| `missing_row` | `MRC_ServiceFee_Check` | last data row omitted (3 rows instead of 4) |
| `extra_sheet` | workbook-level | `_PERTURBATION_EXTRA` sheet appended |

## What to look at

Open `comparison_report.json` and check:
1. `diffs` contains entry with `category: "value"` on `MRC_General_Check` row 2 — proves `value_diff` detected
2. `diffs` contains entry with `category: "font"` on `MRC_Advance_Check` row 2 — proves `font_diff` detected
3. `diffs` contains `category: "structure"` on `MRC_ServiceFee_Check` (dimension change) — proves `missing_row` detected
4. `diffs` contains `category: "structure"` mentioning `_PERTURBATION_EXTRA` — proves `extra_sheet` detected

This is the key gate test: if all 4 show up, the harness is working correctly end-to-end.
