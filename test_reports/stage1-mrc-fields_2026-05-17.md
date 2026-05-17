# Stage 1 — `stage1-mrc-fields` (1.4 字段定义 (fields.zh.md) Fields) Test Report

**Date**: 2026-05-17
**Author**: Copilot CLI agent
**Scope**: 1.4 字段定义 (fields.zh.md) `docs/mrc/fields.{en,zh}.md` — per-column field-level lineage for all 5 MRC sheets (raw table → CTE → projection → Python stamp → render).

## Deliverables

- `docs/mrc/fields.en.md` — NEW, 26 headings (11 H2 + 15 H3), ~45 KB.
- `docs/mrc/fields.zh.md` — NEW mirror, 26 headings, ~36 KB.
- `mkdocs.yml` — added `- 1.4 Fields: mrc/fields.md` under MRC nav.
- `tools/stage_doc_checks.py` — PAIRS extended 15 → 16.

## Per-check matrix

| # | Check | Command | Exit | Verdict |
|---|---|---|---|---|
| 1 | Heading alignment (zh ↔ en) | `python tools/stage_doc_checks.py` | 0 | **PASS** — 16/16 ALIGN OK; fields pair = 26 headings each |
| 2 | Source-citation validity | (same run) | 0 | **PASS** — 614 citations, 0 missing-file, 0 out-of-range (+52 vs 1.3 Sheet 渲染层 (sheets.zh.md) baseline of 562) |
| 3 | pytest | `pytest -q` | 0 | **PASS** — 14/14 |
| 4 | mkdocs build (strict) | `mkdocs build --strict` | 0 | **PASS** — built in 10.02s, no warnings |

## Severity

- **P0**: none.
- **P1**: none.
- **P2**: none.

## § 6.10 compliance

1.4 字段定义 (fields.zh.md) contains **6 figures** (1.4.3 5-layer lineage + 1.4.4–1.4.8 per-sheet lineage diagrams); each figure paired with a 5-bullet textual block. Complex logic (cross-sheet lineage) decomposed into per-sheet diagrams. All diagrams reflect actual existing behavior with source-line citations. **PASS**.

## Field coverage

Per-column lineage tables cover **91 distinct output columns** across 5 sheets (Summary 14 + General 35 + Advance 27 + ServiceFee 8 + AdvInfo 7), each row with: column index, source table.column, transform expression, type/round, NULL/edge notes. 9 gaps surfaced (extends 1.3 Sheet 渲染层 (sheets.zh.md) § 10's 6 gaps with 3 new field-level ones: alias overlap V2/V3, sign convention on Advance diff, `totalservicefee` SUM ordering).

## Gate decision

✅ **PASS** — 1.4 字段定义 (fields.zh.md) cleared, `stage1-mrc-fields` → done.

## Next stage

`stage1-mrc-rules` (1.5 验证规则 (rules.zh.md)): per-validator validation rules — threshold semantics (currently all 0), highlight-vs-not policy decisions (resolves gap 1 + gap 8), pass/fail interpretation per column family, references to 1.4 字段定义 (fields.zh.md) column-level lineage.
