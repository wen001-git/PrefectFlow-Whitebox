# `run_newsystem_mrc.py` — New-system MRC stub runner

> **Status: STUB** — delete this file and replace with a call to the real
> `whitebox/engine/` once Stage 2 implementation (C5 harness green) is in
> place.

---

## Purpose

`tools/run_newsystem_mrc.py` generates a **synthetic** `validation_report.xlsx`
that mimics the five MRC sheets documented in `docs/mrc/1.3-sheets.zh.md`.
Its sole purpose is to allow the **comparison harness pipeline** (C4 orchestrator
+ C5 end-to-end harness) to be built and tested **before** the real whitebox
engine exists.

---

## Usage

```bash
python tools/run_newsystem_mrc.py \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --out-dir runs/newsystem/20260430T120000/ \
    [--mode pristine|perturbed|empty] \
    [--seed 42]
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--servicer` | yes | — | Must be `mrc` (only servicer supported by stub). |
| `--remit-date` | yes | — | Report date, `YYYY-MM-DD`. |
| `--out-dir` | yes | — | Output directory (created if absent). |
| `--mode` | no | `pristine` | Generation mode (see below). |
| `--seed` | no | `42` | RNG seed for deterministic runs. |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Generation or I/O failure |
| `2` | Invalid arguments |

---

## Modes

### `pristine` (default)
Generates deterministic, no-diff content intended to be **cell-identical** to
a hypothetical legacy run with the same `remit-date`. Use this to exercise the
harness "no diff detected" path.

### `perturbed`
Same as `pristine`, but with **four known injected differences** so the harness
can assert it detects each:

| # | ID | Sheet | Description |
|---|---|---|---|
| 1 | `value_diff` | `MRC_General_Check` | `rate` in row 2 changed `0.04 → 0.05` |
| 2 | `font_diff` | `MRC_Advance_Check` | Cell A2 font flipped to `bold=True` |
| 3 | `missing_row` | `MRC_ServiceFee_Check` | Last data row omitted (3 rows instead of 4) |
| 4 | `extra_sheet` | `_PERTURBATION_EXTRA` | Extra worksheet appended to workbook |

A machine-readable manifest of the perturbations is written to
`<out-dir>/perturbations.json`.

### `empty`
Produces a valid XLSX with all five sheets but **no data rows** (header row
only). Used to exercise the harness "all rows missing" path.

---

## Output files

| File | Description |
|---|---|
| `validation_report.xlsx` | The synthetic MRC workbook (5 sheets). |
| `run_metadata.json` | Sidecar with SHA-256, size, sheet stats, timestamps. |
| `perturbations.json` | *(perturbed mode only)* list of injected diff descriptors. |

---

## Sheet names

The five sheets mirror the canonical names from `docs/mrc/1.3-sheets.zh.md`:

1. `MRC_Summary_check`
2. `MRC_General_Check`
3. `MRC_Advance_Check`
4. `MRC_ServiceFee_Check`
5. `MRC_Adv_Info`

---

## When to delete this stub

Delete `tools/run_newsystem_mrc.py`, `tests/tools/test_run_newsystem_mrc.py`,
and this doc once **both** of the following are true:

1. `whitebox/engine/` Stage 2 implementation produces a real
   `validation_report.xlsx`.
2. `stage2-mrc-cell-identity-harness` (C5) passes against a real legacy run.

Replace all call sites with the real engine invocation.
