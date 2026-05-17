# test_reports/stage1-mrc-dataflow-v2-refine_2026-05-17.md

| Field | Value |
|---|---|
| Stage / todo-id | `stage1-mrc-dataflow` (revision v2 — refine pass) |
| Date | 2026-05-17 |
| Trigger | user prompt: "pls refine the 1.2-dataflow.md of MRC, according the diagram rule I just give to you" |
| Run by | agent |

## Scope of this refine pass

Apply the newly-added user-level rule §7 and project-level AGENTS.md §6.10
("Diagram + text co-requirement") to the existing MRC 1.2 数据流层 (1.2-dataflow.zh.md) dataflow doc.

Changes:

1. Added a 5-bullet "Explanation" block under **Figure 1.2.3** (overall
   dataflow flowchart) covering: business purpose, execution flow, input /
   output, key transformations, dependencies / assumptions.
2. Added **5 decomposed per-validator sub-flow diagrams** so each major
   sub-process has its own low-level diagram with its own 5-bullet block:
   - **Figure 1.2.4** — `mrc_check_adv_balance` (V3) sub-flow (in § 4)
   - **Figure 1.2.5** — `mrc_check_general_info` (V2) sub-flow (in § 5)
   - **Figure 1.2.6** — `mrc_summary_check` (V1) sub-flow (in § 6.1)
   - **Figure 1.2.7** — `mrc_service_fee_check` (V4) sub-flow (in § 6.2)
   - **Figure 1.2.8** — `mrc_other_check` (V5) sub-flow (in § 6.3)
3. **Renumbered** the existing validator-to-sheet sequence diagram from
   Figure 1.2.7 → **Figure 1.2.9** to avoid clash with the new V4 diagram,
   and added a 5-bullet explanation block under it.
4. Added a v2 row to the Revision history table in both `.zh.md` and
   `.en.md` documenting this refine pass.

No source-code lines were changed; no SQL re-read needed. All new figure
captions cite previously-verified source line ranges.

## Files modified

- `docs/mrc/dataflow.en.md` — was 338 lines (v1), now larger (v2)
- `docs/mrc/dataflow.zh.md` — was 339 lines (v1), now larger (v2)

No other files changed.

## Tests

| # | Command | Exit code | Verdict | Notes |
|---|---|---|---|---|
| 1 | `python tools/stage_doc_checks.py` | 0 | ✅ PASS | 14/14 PAIRS ALIGN OK; **510 citations PASS** / 0 missing / 0 out-of-range (was 494 in v1; +16 from new figure source citations) |
| 2 | `pytest -q` (in `.venv`) | 0 | ✅ PASS | 14 passed in 2.27s |
| 3 | `mkdocs build --strict` (in `.venv`) | 0 | ✅ PASS | Built in 9.50 seconds, no warnings |

Heading alignment check after the refine: both `1.2-dataflow.zh.md` and
`1.2-dataflow.en.md` still report **19 headings** (no new H2/H3 added — all
additions are figures + paragraphs inside existing sections).

## Failure severity

None. No P0 / P1 / P2 issues.

## Gate decision

✅ All P0 checks PASS. `stage1-mrc-dataflow` remains `done` in SQL.
This refine pass does not require a new SQL todo; it is recorded as a v2
revision of the existing chapter.

## Next stage

Next ready todo: `stage1-mrc-sheets` (1.3 Sheet 渲染层 (1.3-sheets.zh.md) — MRC per-sheet
column-list helpers). User has not yet said "continue".
