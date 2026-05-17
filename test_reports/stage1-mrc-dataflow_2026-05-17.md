# Stage 1 — MRC 1.2 数据流层 (1.2-dataflow.zh.md) (Dataflow) — Test Report

- **Date**: 2026-05-17
- **Scope**: end-of-chapter verification for `docs/mrc/dataflow.{zh,en}.md`
- **Todo**: `stage1-mrc-dataflow`

## Results

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | ✅ 14/14 PAIRS align; **494 citations PASS** / 0 missing-file / 0 out-of-range |
| `pytest -q` | ✅ **14 passed** |
| `mkdocs build --strict` | ✅ Documentation built in ~10s, no errors |

## What this chapter contains

- 9 H2 sections + sub-sections, heading-aligned across zh/en (19 headings each).
- Document header (purpose / audience / revision history) per AGENTS.md § 6.7.
- Two mermaid figures with captions + legend tables per AGENTS.md § 6.9:
  - Figure 1.2.3 — overall MRC validation-report dataflow (flowchart)
  - Figure 1.2.7 — per-`remit_date` validator-to-sheet call sequence (sequenceDiagram + step-by-step explanation)
- Full table list + join topology + emitted-columns catalog for both SQL templates:
  - `mrc_adv_validation` (`servicer_validation_with_portdaily.py:583-632`, 25 columns)
  - `mrc_general_check` (`servicer_validation_with_portdaily.py:635-705`, 27+ columns)
- Inline SQL summary for the other 3 validators:
  - `mrc_summary_check` (1-row aggregate on `port.portmonth`)
  - `mrc_service_fee_check` (per-loan diff, `mrc.portmrcremitloanlevelrecap ⨝ portmonth ⨝ portfunding`)
  - `_mrc_adv_info_sql` + `mrc_other_check` (3-way UNION ALL on `portmrcremit3rdpartyadvances`/`corpadvances`/`escrowadvances`, run twice for MoM)
- **Validator → key → sheet binding table** (§ 7.1): the cell-identity contract for Stage 2.
- 6 explicit assumptions / unresolved gaps, including a notable **CTE-naming asymmetry** between the two SQL templates (`p1=prior, p2=current` vs `p=current, p2=prior`) — documented as-is, not "fixed".

## Sources verified

- `flow/remit_validation/mrc_validation.py:1-158`
- `flow/remit_validation/servicer_validation_with_portdaily.py:583-705` (both SQL templates, end-to-end)
- `flow/remit_validation/remit_validation.py:134-144` (orchestration)
- `util/gen_remit_validation_report.py:1327-1356` (sheet registry)

All file:line citations validated by `stage_doc_checks.py` (494/0/0).

## Bookkeeping

- Wired `docs/mrc/dataflow.md` into `mkdocs.yml` nav under MRC.
- Added `("mrc/1.2-dataflow.zh.md", "mrc/1.2-dataflow.en.md")` to
  `tools/stage_doc_checks.py` PAIRS (now 14 pairs).
- SQL: `stage1-mrc-dataflow` → done.
- Next ready todo: `stage1-mrc-sheets` (depends on 1.2; depended on by
  1.4 fields).
