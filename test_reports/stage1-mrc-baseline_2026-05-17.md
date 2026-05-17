# test_reports/stage1-mrc-baseline_2026-05-17.md

| Field | Value |
|---|---|
| Stage / todo-id | `stage1-mrc-baseline` (chapter 1.6 Baseline XLSX Behavior) |
| Date | 2026-05-17 |
| Trigger | autopilot: only actionable pending todo in MRC chapter set |
| Run by | agent |

## Scope

Author MRC chapter **1.6 Baseline XLSX Behavior** (`docs/mrc/baseline.{zh,en}.md`)
as a code-derived render contract for the frozen
`(MRC, 2026-04-30)` instance, and stand up the placeholder
`baselines/mrc/2026-04-30/` folder for the physical XLSX once
`tools/freeze_baseline.py` exists (covered by separate `mrc-source-baseline`
todo).

## Approach

Pure source-derivation from `gen_remit_validation_report.py` (style block
`:19-86`, helpers `:1157-1177`, `data_type_format` `:1721-1739`,
`header_format` `:1742-1761`, `diff_cell_format` `:1764-1798`, the 5 MRC
column helpers `:1180-1293`, the 5 sheet-registry entries `:1327-1356`),
cross-stitched with already-authored 1.3 Sheet Rendering Layer (sheets.*.md)
§ 4 rendering-mechanics text.

Two confidence tiers per assertion: `[FROM-CODE]` (fully derivable) vs
`[VERIFY]` (needs physical XLSX inspection). A § 9 **Verification
checklist** lists the 12 outstanding `[VERIFY]` items that gate Stage 2
acceptance — they must all be upgraded to `[CONFIRMED]` once
`baselines/mrc/2026-04-30/validation_report.xlsx` is produced.

## Deliverables

| Artifact | Status |
|---|---|
| `docs/mrc/baseline.zh.md` | created, 18.5 KB, 41 headings |
| `docs/mrc/baseline.en.md` | created, 25.5 KB, 41 headings (ALIGN OK) |
| `baselines/.gitkeep` + `baselines/README.md` | created — explains folder layout, links to chapter 1.6 |
| `baselines/mrc/2026-04-30/.gitkeep` | created — placeholder, awaits physical XLSX |
| `mkdocs.yml` | added `1.6 Baseline: mrc/baseline.md` nav entry under Servicers → MRC |
| `tools/stage_doc_checks.py` | added `("mrc/baseline.zh.md", "mrc/baseline.en.md")` to PAIRS |

## Chapter structure (matches existing MRC docs)

1. Document role + Business purpose
2. Scope and conventions (frozen instance, two-tier confidence, out-of-scope)
3. Workbook-level baseline (sheet inventory + tab order, workbook attrs, per-sheet view attrs)
4. Header baseline (common attrs, fill RGB, per-sheet header layout, row height)
5. Body cell baseline per data_type (money, float, date, str, percentage N/A, default attrs)
6. Diff highlight cell baseline (trigger, style, distribution, design exemption for `pandi_diff`)
7. Column widths and miscellaneous body attrs (auto-fit, empty-sheet fallback)
8. Edge cases requiring physical verification (`±inf`, `NaN`, empty money, date None)
9. Verification checklist V1–V12 (gates Stage 2 acceptance)
10. How to produce the physical baseline (tooling contract + verification workflow)
11. Source citation index

## Verification

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | **18/18 ALIGN OK** (added pair: `mrc/baseline.zh.md` vs `mrc/baseline.en.md`, 41 headings each) + **734 citations PASS** (up from 698 — 36 new source-range cites in chapter 1.6) |
| `pytest -q` | **14 passed in 2.26s** |
| `mkdocs build --strict` | No content warnings (only pre-existing Material framework banner) |
| `mkdocs.yml` nav | new entry visible under Servicers → MRC → 1.6 Baseline |

## Cross-references introduced / consumed

- **Consumed**: 1.3 Sheet Rendering Layer (sheets.{zh,en}.md) § 4 (rendering mechanics text), 1.5 Validation Rules (rules.{zh,en}.md) § 3 (threshold/coerce semantics), 1.4 Field Definitions (fields.{zh,en}.md) § 5 gap 1 (`intrate_*` float vs percentage decision)
- **Introduced**: every prior MRC chapter referenced `1.6 Baseline XLSX Behavior (baseline.{zh,en}.md)` for the `±inf` rendering question and the cell-identity acceptance criterion — those pointers now resolve to actual content (no `[TBD]` placeholders any longer).

## Known follow-ups (carried out of scope)

- `tools/freeze_baseline.py` — produces the physical XLSX; belongs to the
  `mrc-source-baseline` todo (blocked on having a thin Redshift-adapter
  shim against the frozen Parquet snapshot).
- `tools/inspect_baseline.py` — runs the § 9 V1–V12 checks against the
  physical XLSX and back-fills this chapter.
- Stage 1 → Stage 2 gate (`stage1-mrc-review` + `gate-decide`) — requires
  user walk-through; cannot be agent-driven.

## Maintenance contract

- Any change to `gen_remit_validation_report.py:19-86` (style block) must
  trigger a re-review of § 4–§ 6 of this chapter.
- Any change to the 5 column helpers (`:1180-1293`) must trigger a
  re-review of § 3.1 (sheet inventory) + § 4.3 (header layout) + § 6.3
  (highlight distribution).
- When the physical baseline lands: upgrade § 9 to `[CONFIRMED]`, bump
  Revision history to v2, append a record to `decisions.md`, and re-run
  `tools/stage_doc_checks.py` + `mkdocs build --strict` + `pytest -q`.
