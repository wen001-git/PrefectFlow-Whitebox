# Stage 1 — MRC 1.0 章节地图与范围 (toc.zh.md) (TOC) — Test Report

- **Date**: 2026-05-17
- **Scope**: end-of-chapter verification for `docs/mrc/toc.{zh,en}.md`
- **Todo**: `stage1-mrc-toc`

## Results

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | ✅ 12/12 PAIRS align; **320 citations PASS** / 0 missing-file / 0 out-of-range |
| `pytest -q` | ✅ **14 passed** |
| `mkdocs build --strict` | ✅ Documentation built in ~10s, no errors |

## What this chapter contains

- 11 H2 sections, heading-aligned across zh/en
- Document header (purpose / audience / revision history) per AGENTS.md § 6.7
- No mermaid figures, so AGENTS.md § 6.9 (legend rule) does not apply
- Lists the 5 MRC sheets, 5 validators, 2 SQL templates, orchestration entry points, and full source-citation index
- Forward-pointer chapter map (1.1 → 1.7)
- Cross-servicer placeholders section per v9.1 pivot

## Correction recorded

**MRC has 5 validators (incl. `mrc_other_check`), not 4.** Earlier plan v9.1
drafts and 2 checkpoint summaries claimed "4 validators, no
`mrc_other_check`" — this was wrong. Source-verified mapping:

| Validator (Python `@task`) | Sheet | Source citation |
|---|---|---|
| `mrc_summary_check` | MRC_Summary_check | `mrc_validation.py:8-36` |
| `mrc_check_general_info` | MRC_General_Check | `mrc_validation.py:57-72` |
| `mrc_check_adv_balance` | MRC_Advance_Check | `mrc_validation.py:39-54` |
| `mrc_service_fee_check` | MRC_ServiceFee_Check | `mrc_validation.py:75-102` |
| `mrc_other_check` | MRC_Adv_Info | `mrc_validation.py:136-158` |

Propagation:
- ✅ `docs/_status/servicers.yaml` notes updated
- ✅ `decisions.md` entry appended
- ✅ recorded prominently in `docs/mrc/toc.{zh,en}.md` § 5 and revision history
- ✅ `docs/_status/servicers-registry.{zh,en}.md` already said "5" — no change needed
- ✅ `plan.md` (current v6) has no servicer matrix referencing the old count — no change needed

## Minor fixes during this round

- Off-by-one citation: `mrc_db.py` is 14 lines, not 15. Fixed `1-15` → `1-14`
  and `7-15` → `7-14` in both zh/en TOC files.
- Wired `docs/mrc/toc.md` into `mkdocs.yml` nav under MRC.
- Added `("mrc/toc.zh.md", "mrc/toc.en.md")` to `tools/stage_doc_checks.py`
  PAIRS (now 12 pairs).
