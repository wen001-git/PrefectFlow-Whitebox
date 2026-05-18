# `compare_validation.py` — Comparison Orchestrator Operator Guide

> **Version**: 1.0.0 — Round 2 C4
>
> **Status**: ACTIVE — used as the G2b-LIVE gate harness
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-18 | Copilot CLI agent | v1 — initial version (Round 2 C4). |

---

## 1. Purpose

`tools/compare_validation.py` is the **single-command** comparison orchestrator for
the G2b-LIVE validation gate. Given two `validation_report.xlsx` files — one produced
by the legacy PrefectFlow engine (C2) and one by the new whitebox system (C3) — it:

1. Calls the C1 cell-level diff engine (`xlsx_diff.diff_workbooks`) directly as a
   Python import (faster, better error propagation than subprocess).
2. Enriches the diff output with run-metadata context from both runs.
3. Emits a **machine-readable verdict** (`verdict.json`) with pass/fail semantics,
   operator warnings, and human-readable next-step hints.
4. Produces an **HTML report** (`comparison_report.html`) enriched with run-context.
5. Logs all steps to `comparison_report.log`.

**One command produces a complete audit trail**: HTML + JSON + verdict + log.

**Cross-refs**:
- Plan § 9 / § 9.3 row C4 (`plan.md`)
- `docs/stage2/10.0-validation-strategy.{zh,en}.md` — strategy pivot rationale
- `AGENTS.md` § 6.11 — living-doc rule
- C1: `tools/docs/xlsx_diff-help.txt`
- C2: `tools/docs/run_legacy_mrc.md`
- C3: `tools/docs/run_newsystem_mrc.md`
- A5 operator runbook: `tools/docs/g2a-operator-runbook.en.md`

---

## 2. Two modes

### Mode A — compare (manual paths)

Use this when you already have two XLSX files and want to compare them directly.

```bash
python tools/compare_validation.py compare \
    --legacy-xlsx  runs/legacy/20260430/validation_report.xlsx \
    --new-xlsx     runs/newsystem/20260430/validation_report.xlsx \
    --report-dir   runs/comparison/20260430/ \
    [--legacy-metadata runs/legacy/20260430/run_metadata.json] \
    [--new-metadata    runs/newsystem/20260430/run_metadata.json] \
    [--float-tolerance 0.0] \
    [--ignore-style] [--ignore-format] [--ignore-row-heights] \
    [--summary-only] \
    [--quiet]
```

**When to use**: post-hoc comparison; you ran C2 and C3 separately and want to diff
the results now.

#### Required options

| Option | Description |
|---|---|
| `--legacy-xlsx` | Path to the legacy `validation_report.xlsx`. |
| `--new-xlsx` | Path to the new-system `validation_report.xlsx`. |
| `--report-dir` | Output directory (created if absent). |

#### Optional options

| Option | Default | Description |
|---|---|---|
| `--legacy-metadata` | auto-detect | Path to legacy `run_metadata.json` sidecar. |
| `--new-metadata` | auto-detect | Path to new-system `run_metadata.json` sidecar. |
| `--float-tolerance` | `0.0` | Tolerance for float comparisons. |
| `--ignore-style` | off | Suppress font/fill/border/alignment diffs. |
| `--ignore-format` | off | Suppress number-format diffs. |
| `--ignore-row-heights` | off | Suppress row-height diffs. |
| `--summary-only` | off | Omit per-cell diff details from HTML/JSON. |
| `--servicer` | None | Servicer code (for verdict context). |
| `--remit-date` | None | Remit date (for verdict context). |
| `--new-mode` | None | New-system mode, for warning logic. |
| `--quiet` | off | Suppress stdout logging. |

---

### Mode B — auto (invoke C2 + C3 + diff)

Use this for a fully automated comparison run from scratch.

```bash
python tools/compare_validation.py auto \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --report-dir runs/comparison/20260430/ \
    [--source-repo ../PrefectFlow] \
    [--new-mode pristine|perturbed|empty] \
    [--skip-legacy] [--legacy-xlsx <existing-path>] \
    [--skip-new]    [--new-xlsx    <existing-path>] \
    [--dry-run] \
    [--quiet]
```

**When to use**: full automated gate run; orchestrates C2 + C3 + C1 in order.

#### Orchestration flow

```
auto
 │
 ├─ Step 1: resolve legacy XLSX
 │    ├─ if --skip-legacy: reuse --legacy-xlsx
 │    └─ else: invoke  tools/run_legacy_mrc.py  (C2, subprocess)
 │               → <report-dir>/legacy/validation_report.xlsx
 │                 <report-dir>/legacy/run_metadata.json
 │
 ├─ Step 2: resolve new XLSX
 │    ├─ if --skip-new: reuse --new-xlsx
 │    └─ else: invoke  tools/run_newsystem_mrc.py  (C3, subprocess)
 │               → <report-dir>/newsystem/validation_report.xlsx
 │                 <report-dir>/newsystem/run_metadata.json
 │
 └─ Step 3: compare (C1 import)
       → <report-dir>/comparison_report.html
         <report-dir>/comparison_report.json
         <report-dir>/verdict.json
         <report-dir>/comparison_report.log
```

#### Skip flags (for iteration)

| Flag | Meaning |
|---|---|
| `--skip-legacy --legacy-xlsx <p>` | Reuse existing legacy XLSX; skip C2 invocation. |
| `--skip-new --new-xlsx <p>` | Reuse existing new XLSX; skip C3 invocation. |
| Both together | Equivalent to `compare` subcommand. |

#### Dry-run

```bash
python tools/compare_validation.py auto \
    --servicer mrc --remit-date 2026-04-30 \
    --report-dir /tmp/out \
    --dry-run
```

Prints the orchestration plan (paths, commands, thresholds) without executing anything.
Always exits 0.

---

## 3. Output files

All output is written inside `--report-dir`:

| File | Description |
|---|---|
| `comparison_report.html` | C1 HTML diff report, enriched with run-context banner. |
| `comparison_report.json` | C1 JSON report + `legacy_run` / `new_run` metadata embedded. |
| `verdict.json` | Machine-readable top-level pass/fail summary (see § 4). |
| `comparison_report.log` | Combined log from C2 + C3 + diff steps. |

In auto mode, sub-outputs are:

| Path | Description |
|---|---|
| `<report-dir>/legacy/validation_report.xlsx` | Legacy output from C2. |
| `<report-dir>/legacy/run_metadata.json` | C2 sidecar. |
| `<report-dir>/newsystem/validation_report.xlsx` | New-system output from C3. |
| `<report-dir>/newsystem/run_metadata.json` | C3 sidecar. |

---

## 4. Verdict semantics

### Exit codes

| Code | Meaning |
|---|---|
| `0` | `PASS` — workbooks are cell-identical. |
| `1` | `MINOR_DIFFS` — minor style/format diffs only; no value or structural diffs. |
| `2` | `MAJOR_DIFFS` — value, formula, structure, or merged-cell diffs detected. |
| `3` | `ERROR` — I/O error, subprocess failure, or missing XLSX path. |

### Verdict strings

| Verdict | Exit code | One-line stdout |
|---|---|---|
| `PASS` | 0 | `✅ PASS` |
| `MINOR_DIFFS` | 1 | `🟡 MINOR_DIFFS (major=0, minor=N)` |
| `MAJOR_DIFFS` | 2 | `🔴 MAJOR_DIFFS (major=N, minor=M)` |
| `ERROR` | 3 | `💥 ERROR` |

### What counts as MAJOR

The following diff categories are **major** (trigger exit 2 / `MAJOR_DIFFS`):
- `value` — cell value changed
- `formula` — formula changed
- `structure` — sheet added/removed/reordered; dimensions changed
- `merged_cells` — merged cell ranges changed

Everything else (font, fill, border, alignment, number format, freeze panes, column
widths, row heights, sheet tab color) is **minor**.

---

## 5. Reading `verdict.json`

Example `verdict.json`:

```json
{
  "exit_code": 2,
  "generated_at": "2026-04-30T14:23:11.123456+00:00",
  "legacy_run": {
    "path": "runs/legacy/20260430/validation_report.xlsx",
    "sha256": "a1b2c3...",
    "source_repo_sha": "7058ec8",
    "started_at": "2026-04-30T10:00:00+00:00"
  },
  "new_run": {
    "mode": "pristine",
    "path": "runs/newsystem/20260430/validation_report.xlsx",
    "sha256": "d4e5f6...",
    "started_at": "2026-04-30T10:05:00+00:00"
  },
  "next_steps": [
    "Investigate engine/transform; cite ch 1.4 / 1.5 for expected behavior."
  ],
  "remit_date": "2026-04-30",
  "servicer": "mrc",
  "summary": {
    "identical": false,
    "major_diff_count": 3,
    "minor_diff_count": 1,
    "per_sheet": [
      {"extra": false, "major": 1, "minor": 0, "missing": false, "sheet": "MRC_General_Check"},
      ...
    ]
  },
  "tool_version": "1.0.0",
  "verdict": "MAJOR_DIFFS",
  "warnings": []
}
```

### Warnings

Automatically surfaced (non-blocking):

| Condition | Warning text |
|---|---|
| Legacy `source_repo_dirty == true` | "legacy repo had uncommitted changes; result may not be reproducible" |
| Gap between runs > 1 hour | "Redshift may have drifted between runs (gap = N min …)" |
| `new-mode=pristine` + no major diffs | "harness self-test passed (pristine mode, no major diffs)" |
| `new-mode=perturbed` + missing perturbation IDs | "harness may have missed expected perturbations: [...]" |
| `--ignore-style` used | "--ignore-style was used; font/fill/border/alignment diffs are suppressed" |

### Next-step hints

Automatically generated based on verdict + diff categories:

| Situation | Hint |
|---|---|
| PASS | "Cell-identity confirmed. Safe to ship." |
| MINOR_DIFFS | "Review HTML report; minor style diffs may be acceptable …" |
| MAJOR_DIFFS — value category | "Investigate engine/transform; cite ch 1.4 / 1.5 …" |
| MAJOR_DIFFS — structure category | "Sheet missing/extra → check sheet renderer registration." |
| ERROR | "Read comparison_report.log; verify creds and source-repo path." |

---

## 6. Reading the HTML report

Open `comparison_report.html` in a browser.

- **Run context banner** (blue box): servicer, remit date, run start times, legacy source SHA.
- **Per-sheet summary table**: major/minor counts per sheet; missing/extra flags.
- **Expandable per-sheet detail sections**: click to expand; each row shows severity,
  row/column address, diff category, legacy value, new value.
- **Color coding**: red background = major diff; yellow background = minor diff.

---

## 7. Integration with G2b-LIVE gate

The G2b-LIVE gate (`progress.md` gate table) requires a comparison run evidence per
implementation PR. The recommended workflow:

```bash
# 1. Run legacy (operator, requires VPN + Vault — see tools/docs/run_legacy_mrc.md)
python tools/run_legacy_mrc.py \
    --servicer mrc --remit-date 2026-04-30 \
    --out-dir runs/legacy/$(date +%Y%m%dT%H%M%S)/

# 2. Compare legacy vs new-system (in CI or locally)
python tools/compare_validation.py auto \
    --servicer mrc --remit-date 2026-04-30 \
    --skip-legacy --legacy-xlsx runs/legacy/<timestamp>/validation_report.xlsx \
    --new-mode pristine \
    --report-dir runs/comparison/<timestamp>/

# 3. Gate check — exit code drives CI pass/fail
# exit 0 = PASS, exit 1 = minor (review), exit 2 = MAJOR (block), exit 3 = error
```

The `verdict.json` and `comparison_report.html` are attached to the PR as evidence.

---

## 8. Cross-references

| Resource | What it covers |
|---|---|
| `plan.md` § 9 | Strategy pivot rationale; C1–C6 todo spec |
| `plan.md` § 9.3 | C4 full spec (this tool) |
| `docs/stage2/10.0-validation-strategy.{zh,en}.md` | Temporary vs ideal approach; G2b-LIVE definition |
| `tools/docs/xlsx_diff-help.txt` (C1) | Cell-level diff options; major vs minor categories |
| `tools/docs/run_legacy_mrc.md` (C2) | Legacy runner prerequisites and credential setup |
| `tools/docs/run_newsystem_mrc.md` (C3) | New-system stub modes and perturbation manifest |
| `tools/docs/g2a-operator-runbook.en.md` (A5) | VPN / Vault pre-flight checklist |
| `AGENTS.md` § 6.11 | Living-doc rule (incremental refinement policy) |
