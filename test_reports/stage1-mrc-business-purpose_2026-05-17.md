# test_reports/stage1-mrc-business-purpose_2026-05-17.md

| Field | Value |
|---|---|
| Stage / todo-id | `stage1-mrc-business-purpose` (per-sheet business-intent intro) |
| Date | 2026-05-17 |
| Trigger | user prompt: "Please enhance both `sheets.md` and `fields.md` by adding a business-oriented introduction section for every Validation Report sheet" |
| Run by | agent |

## Scope

For every MRC Validation Report sheet (5 sheets), add a dedicated
**Business purpose / 业务用途** subsection at the head of its chapter in
both rendering doc and field-lineage doc, both languages.

| File | Sheet H2s receiving the new block |
|---|---|
| `docs/mrc/sheets.zh.md` | § 5–9 (`MRC_Summary_check`, `MRC_General_Check`, `MRC_Advance_Check`, `MRC_ServiceFee_Check`, `MRC_Adv_Info`) |
| `docs/mrc/sheets.en.md` | same |
| `docs/mrc/fields.zh.md` | § 4–8 (same 5 sheets, field-lineage chapters) |
| `docs/mrc/fields.en.md` | same |

Total: **5 sheets × 4 files = 20 subsection blocks** inserted.

## Convention adopted

- Heading: `### 业务用途 / Business purpose` (ZH side) /
  `### Business purpose / 业务用途` (EN side). **Unnumbered** so existing
  subsection numbering (X.1, X.2 …) is preserved and no cross-reference
  needs updating.
- Hidden idempotency marker on the preceding line:
  `<!-- BUSINESS-PURPOSE-V1 -->` — re-running the inserter is a no-op.
- Content shape (per block, ~10–18 lines):
    - opening one-paragraph framing of the sheet's mission
    - **业务问题 / Business questions answered** (3–4 bullets)
    - **数据口径 / Population**
    - **典型读者 / Audience**
    - **高亮/设计理由 / Design intent + highlight rationale**
      (per-column business reasoning where applicable)
    - **常见失败场景 / Common failure scenarios** (concrete real-world
      examples)
    - **风险 / 对账动机 / Risk and reconciliation motivation**
- Cross-references to other MRC chapters use the three-element form
  established in `_chapter-index.md` (e.g.
  `1.4 字段定义 (fields.zh.md)` / `1.6 Baseline XLSX Behavior
  (baseline.en.md)`).
- Differentiation between `sheets.*.md` and `fields.*.md` content:
  `sheets` focuses on *what the page is and who reads it*; `fields`
  focuses on *what per-column lineage tells you and who maintains it*.
  Each section includes a **Division with sheets/fields** bullet making
  the split explicit.

## Tooling (kept in `tools/`)

| Script | Purpose |
|---|---|
| `tools/insert_business_purpose.py` | Idempotent inserter; carries the per-sheet bilingual content as Python dicts (`SHEETS_ZH`, `SHEETS_EN`, `FIELDS_ZH`, `FIELDS_EN`) |
| `tools/clean_business_purpose_label.py` | Post-pass that strips the redundant first-bullet label that duplicated the H3 heading |

Both scripts are idempotent (re-runs report 0 changes).

## Verification

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | **17/17 ALIGN OK + 698 citations PASS** (each of 4 docs gained 5 symmetric H3 headings on EN+ZH sides) |
| `pytest -q` | **14 passed in 2.36s** |
| `mkdocs build --strict` | No content warnings (only pre-existing Material framework banner) |
| Idempotency: re-run inserter | `inserted 0` on all 4 files |
| Idempotency: re-run cleanup | `stripped 0` on all 4 files |
| Manual spot-check (sheets.zh § 5, fields.en § 6) | Renders cleanly; H3 visible in outline; content flows naturally |

## Business content per sheet (one-line summary)

| Sheet | Business purpose (one line) |
|---|---|
| `MRC_Summary_check` | Portfolio-level rollup — first sniff test, 0 highlights by design |
| `MRC_General_Check` | Primary per-loan reconciliation — 7 highlighted diff dimensions, source of ~80% ops tickets |
| `MRC_Advance_Check` | Per-loan advance-bucket reconciliation — most cash-/accounting-sensitive step |
| `MRC_ServiceFee_Check` | Only revenue-side page — service fee A/P invoice check |
| `MRC_Adv_Info` | Bucket × txn-code activity trend with MoM — anomaly / pattern-drift detection |

## Why "unnumbered" subsection (design decision)

Two alternatives considered:
1. **Renumber existing X.1 → X.2 etc.** — would break dozens of intra-doc
   citations and risk breaking cross-doc references in `fields.zh.md` ↔
   `sheets.zh.md` pairs (Stage 2 cell-identity contract).
2. **Insert as X.0** — unusual numbering, would confuse readers.
3. **Unnumbered `### Business purpose`** (chosen) — appears in mkdocs
   outline as a peer to X.1 / X.2, requires zero renumbering, satisfies
   the user's outline-visibility intent.

## Open follow-ups (deliberately out of scope)

- The new bullets cite `1.6 Baseline XLSX Behavior (baseline.{zh,en}.md)`
  for the `±inf` rendering gap; baseline.* is not yet authored — citation
  will resolve once `stage1-mrc-baseline` runs. No rework needed.
- The cleanup script left a small cosmetic indent (2-space leading on
  continuation lines of the opening paragraph) — Markdown renders this
  identically; no action.

## Maintenance contract

When editing the business-purpose block in any one file:
1. Mirror the edit in the paired language file (EN ↔ ZH) to keep
   `stage_doc_checks.py` PAIRS alignment.
2. Mirror the edit in `sheets.*.md` ↔ `fields.*.md` only when the change
   is content-substantive — wording differences between the two file
   types are intentional (rendering vs lineage angle).
3. Re-run `tools/stage_doc_checks.py` + `mkdocs build --strict` + `pytest -q`
   before considering the edit complete.
