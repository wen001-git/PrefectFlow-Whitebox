# Stage 1 — MRC 1.1 原始数据层 (rawdata.zh.md) (Raw data) — Test Report

- **Date**: 2026-05-17
- **Scope**: end-of-chapter verification for `docs/mrc/rawdata.{zh,en}.md`
- **Todo**: `stage1-mrc-rawdata`

## Results

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | ✅ 13/13 PAIRS align; **412 citations PASS** / 0 missing-file / 0 out-of-range |
| `pytest -q` | ✅ **14 passed** |
| `mkdocs build --strict` | ✅ Documentation built in ~10s, no errors |

## What this chapter contains

- 10 H2 sections + sub-sections, heading-aligned across zh/en (14 headings each).
- Document header (purpose / audience / revision history) per AGENTS.md § 6.7.
- One mermaid figure (Figure 1.1.5 — MRC ingestion call graph) with caption
  and legend table per AGENTS.md § 6.9.
- Resolves the un-known `fctrdt` value left open in 1.0 章节地图与范围 (toc.zh.md):
  **`fctrdt = 2026-05-01`**, **`fctrdt_1m = 2026-04-01`** at baseline.
- Enumerates the **13 ingested `mrc.portmrcremit*` tables** and the
  sheet→table / sheet→loanid-column / column-rename mappings.
- Identifies the **5 raw tables** (4 `mrc.*` + 2 aux `port.*`) actually
  consumed by the 5 MRC validators (out of 13 ingested).
- Notes that the wider `basic_data_monthly_loan_common_base` ETL is
  **not** on the Validation-Report path.
- Records 6 explicit open assumptions / unresolved gaps to be addressed
  in sub-chapters 1.2, 1.4, and 1.6.

## Sources verified

- `tasks/servicer_data/remit_config.py:8, 178-225`
- `tasks/servicer_data/remit_utils.py:280-307, 546-549, 574-624, 627-633, 636-757`
- `tasks/servicer_data/monthly_task.py:49-110`
- `flow/remit_validation/utils.py:7-11`
- `flow/remit_validation/mrc_db.py:1-14`
- `flow/remit_validation/mrc_validation.py:8-158`
- `flow/basic_data/transfer_monthly_data_config/monthly_data_loan_common_config.py:1426-1623`

All file:line citations validated by `stage_doc_checks.py` (412/0/0).

## Bookkeeping

- Wired `docs/mrc/rawdata.md` into `mkdocs.yml` nav under MRC.
- Added `("mrc/rawdata.zh.md", "mrc/rawdata.en.md")` to
  `tools/stage_doc_checks.py` PAIRS (now 13 pairs).
- SQL: `stage1-mrc-rawdata` → done.
- Next ready todo: `stage1-mrc-dataflow` (depends on 1.1; depended on by
  1.3 sheets).
