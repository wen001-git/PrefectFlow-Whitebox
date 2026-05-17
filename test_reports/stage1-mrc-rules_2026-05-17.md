# Stage 1 — `stage1-mrc-rules` (1.5 验证规则 (rules.zh.md)) — test report

- **Date**: 2026-05-17
- **Scope**: MRC chapter sub-1.5 验证规则 (rules.zh.md) — rule catalog (`docs/mrc/rules.en.md` + `docs/mrc/rules.zh.md`)
- **Trigger**: SQL todo `stage1-mrc-rules` flipped to `in_progress` after 1.4 字段定义 (fields.zh.md) delivery.

## Files produced / modified

| File | Change | Note |
|---|---|---|
| `docs/mrc/rules.en.md` | NEW | 11 H2 + 18 H3 = 29 headings; ~35 KB; 9 OPEN-POLICY entries; 5 mermaid figures |
| `docs/mrc/rules.zh.md` | NEW | Same 29-heading skeleton; ~25 KB; full prose mirror in Chinese (H2/H3 names kept English, matching dataflow/sheets/fields convention) |
| `mkdocs.yml` | MOD | added `- 1.5 Rules: mrc/rules.md` under MRC nav (after 1.4) |
| `tools/stage_doc_checks.py` | MOD | PAIRS extended 16 → 17 |

## Test matrix

| Check | Result | Detail |
|---|---|---|
| `python tools/stage_doc_checks.py` heading alignment | ✅ 17/17 ALIGN OK | new line: `mrc/rules.zh.md vs mrc/rules.en.md (29 headings)` |
| `python tools/stage_doc_checks.py` source citations | ✅ 696 PASS / 0 missing-file / 0 out-of-range | up from 614 (= +82 new citations from 1.5 验证规则 (rules.zh.md)) |
| `pytest -q` | ✅ 14 passed in 2.30s | unchanged |
| `mkdocs build --strict` | ✅ Documentation built in 11.14 seconds | no warnings; new 1.5 page rendered in both EN and ZH |

## § 6.10 compliance (all 5 figures)

Each of the 5 mermaid figures in this chapter ships with a 5-bullet explanation block: **Business purpose / Execution flow / Input / Output / Key transformations / Dependencies / Assumptions**:

- Figure 1.5.3 — MRC rule application pipeline ✅
- Figure 1.5.4 — V1 `mrc_summary_check` decision tree ✅
- Figure 1.5.5 — V2 `mrc_check_general_info` per-cell decision tree ✅
- Figure 1.5.6 — V3 `mrc_check_adv_balance` per-bucket decision tree ✅
- Figure 1.5.7 — V4 `mrc_service_fee_check` per-cell decision tree ✅
- Figure 1.5.8 — V5 `mrc_other_check` per-row decision tree ✅

## Severity classification

- **P0 (must-fix)**: none
- **P1**: none
- **P2**: 9 `OPEN-POLICY` entries explicitly tagged for 1.7 用户走读评审 review — these are *deliverable* outputs of 1.5 验证规则 (rules.zh.md), not defects

## Gate decision

✅ **PASS** — 1.5 验证规则 (rules.zh.md) delivered. Test matrix green. 9 explicit policy questions handed off to 1.7 用户走读评审. Next: `stage1-mrc-baseline` (1.6 Baseline XLSX 行为 (baseline.zh.md) — capture 2026-04-30 baseline XLSX state per 1.3 Sheet 渲染层 (sheets.zh.md) rendering pipeline and 1.5 验证规则 (rules.zh.md) rule taxonomy).
