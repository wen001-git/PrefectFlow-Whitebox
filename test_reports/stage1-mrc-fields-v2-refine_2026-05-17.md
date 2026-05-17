# test_reports/stage1-mrc-fields-v2-refine_2026-05-17.md

| Field | Value |
|---|---|
| Stage / todo-id | `stage1-mrc-fields` (revision v2 — refine pass) |
| Date | 2026-05-17 |
| Trigger | user prompt: "pls enhance the field.md documentation to improve business explainability and reverse-engineering transparency" |
| Run by | agent |

## Scope of this refine pass

Enrich every per-sheet field lineage table in MRC 1.4 字段定义 (fields.zh.md) (`fields.en.md`
and `fields.zh.md`) with two new columns to make business and computational
semantics fully explainable to future developers, reviewers, data analysts,
validators, and Stage 2 rewrite efforts.

Changes:

1. **Row format upgrade** (§ 2 in both files): the per-column row schema
   went from 6 columns to 8 columns:

   Old: `# | Output column | Source | Transform | Type / round | Notes`

   New: `# | Output column | Business Meaning | Source | Transform | Calculation Logic | Type / round | Notes`

2. **`Business Meaning` column** added between `Output column` and `Source`:
   - explains what the field represents in the Validation Report
   - states how business users / analysts interpret or use it
   - documents important business context, assumptions, sign conventions
   - calls out NULL semantics, INFO-only vs highlighted, naming asymmetries

3. **`Calculation Logic` column** added between `Transform` and `Type / round`:
   - restates Transform in natural language / pseudo-code / set notation
   - declared notation key in § 2: `∑` SUM, `∩` AND, `∪` OR, `−` minus,
     `⟶` mapping, `≔` assignment
   - documents fallback ladders, NULL-propagation paths, sign conventions,
     edge cases (`±inf`, `NaN`), snapshot-existence guards
   - marks assumptions and unresolved gaps explicitly; no invented logic

4. **All 5 per-sheet tables** in both languages rewritten to 8 cols:
   - V1 § 4.1 `MRC_Summary_check` — 14 rows
   - V2 § 5.1 `MRC_General_Check` — 35 rows (largest; includes V2 deferred
     NULL-mask risk on cols 21/24, fallback ladder on col 27)
   - V3 § 6.1 `MRC_Advance_Check` — 27 rows (includes opposite-sign
     `+` convention on diff cols, `recov` vs `rec` naming asymmetry,
     `coalesce(total, rec+nonrec)` fallback)
   - V4 § 7.1 `MRC_ServiceFee_Check` — 8 rows (includes silent
     no-highlight when `p.servicefee` is NULL)
   - V5 § 8.1 `MRC_Adv_Info` — 7 rows (includes 4-case `amt_MoM`
     `±inf` / `NaN` enumeration)
   - **Total enriched: 91 rows × 2 languages = 182 row-edits**

5. **Cross-references preserved** — all existing `:LINE` citations to
   `mrc_validation.py` / `servicer_validation_with_portdaily.py` kept
   verbatim; no source-code lines re-read or changed.

## Files modified

- `docs/mrc/fields.en.md` — was ~436 lines (v1), enriched to 8-col format
- `docs/mrc/fields.zh.md` — same enrichment mirrored in Chinese prose
  (English headers + technical labels kept verbatim per project convention)

No source code changed. No SQL re-read. No new pytest / mkdocs tests added.

## Verification

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | **17/17 ALIGN OK**, fields.zh.md vs fields.en.md = 26 headings (adding table columns doesn't change heading depth) |
| Citations | **698 PASS / 0 missing-file / 0 out-of-range** (was 697 after EN pass; +1 from legitimate re-citation in V2 row 35) |
| `pytest -q` | **14 passed in 2.49s** |
| `mkdocs build --strict` | **No warnings**; unicode notation `∑ ∩ ∪ − ⟶ ≔` renders fine in both languages |

## Notation conventions adopted

Declared once in § 2 and used uniformly across all 91 × 2 Calculation Logic
cells:

| Symbol | Meaning |
|---|---|
| `∑` | SUM aggregate |
| `∩` | logical AND |
| `∪` | logical OR |
| `−` | subtraction / set difference |
| `⟶` | mapping |
| `≔` | assignment |

Pseudo-code conventions:

- `IF (cond) THEN x ELSE y` for SQL `CASE` blocks
- `first-non-NULL(a, b, …)` for `coalesce(…)`
- `NULL → 0` for explicit `coalesce(x, 0)` NULL masking
- Source-line `:LINE` suffix preserved from Transform col so citations stay
  one-click traceable

## Cross-chapter pointers re-validated (no new claims invented)

- V2 col 9 `totalservicefee` NULL-row exclusion → 1.5 验证规则 (rules.zh.md) § 10 政策 8 (existing)
- V2 col 21 / col 24 NULL→0 masquerade → 1.5 验证规则 (rules.zh.md) § 10 政策 5 (existing)
- V2 col 27 monthly→remit fallback ladder → 1.5 验证规则 (rules.zh.md) § 10 政策 3 (existing)
- V3 col 14 `recov` vs `rec` naming asymmetry → 1.3 Sheet 渲染层 (sheets.zh.md) § 10 gap 3 (existing)
- V3 cols 9/14/19/24 opposite-sign **+** diff convention → 1.3 Sheet 渲染层 (sheets.zh.md) § 10 (existing)
- V4 col 7 silent no-highlight when `p.servicefee` NULL → 1.5 R3 / 政策 6 (existing)
- V5 col 6 `amt_MoM` `±inf` / `NaN` 4-case enumeration → 1.3 Sheet 渲染层 (sheets.zh.md) § 10 gap 5 (existing)

All gaps pre-existed; this refine pass exposes them inline in the lineage
tables instead of forcing readers to cross-jump to 1.3 Sheet 渲染层 (sheets.zh.md) / 1.5.

## Out of scope

- Did not update `progress.md` item 19 (1.4 字段定义 (fields.zh.md) already marked done in
  the original `stage1-mrc-fields_2026-05-17.md` test report)
- Did not retitle headings; H1 / H2 / H3 / H4 structure unchanged
- Did not edit any other chapter (1.0–1.3, 1.5)

## Sign-off

Refine pass closes the user's "business explainability + reverse-engineering
transparency" requirement on 1.4 字段定义 (fields.zh.md). 1.4 字段定义 (fields.zh.md) v2 is now the
canonical lineage reference for Stage 2 MRC rewrite.
