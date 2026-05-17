# test_reports/stage1-mrc-xref-readability_2026-05-17.md

| Field | Value |
|---|---|
| Stage / todo-id | `stage1-mrc-xref-readability` (cross-chapter readability refine) |
| Date | 2026-05-17 |
| Trigger | user prompt: "Please improve the MRC documentation cross-reference system for readability and long-term maintainability" |
| Run by | agent |

## Scope

Apply a project-wide convention so that every reference to an MRC chapter
contains three elements:

1. Numeric ID (`1.4`)
2. Full chapter title — bilingual where appropriate (`Field Definitions` /
   `字段定义`)
3. Markdown filename matching the current document's language
   (`1.4-fields.zh.md` in ZH docs, `1.4-fields.en.md` in EN docs)

Touched files (per user-confirmed scope):

- `docs/mrc/*.md` × 12
- `progress.md`, `plan.md`
- `test_reports/stage1-mrc-*.md` × 8

Untouched (explicit out-of-scope):

- `docs/_archived/pre-mrc-pivot/*.md` (historical)
- `test_reports/stage1-carrington_*.md` / `stage1-shellpoint_*.md` /
  `stage1-overall-flow_*.md` (other-servicer chapters)
- `AGENTS.md`, `decisions.md`, `README.md`, checkpoints

## Changes

### 1. New canonical-truth files

- **`docs/mrc/_chapter-index.md`** — single source of truth: 8-row chapter
  table (1.0–1.7) with EN title, ZH 标题, file basename, one-line scope;
  citation-format conventions (whole-chapter, section, self-ref, compact
  form, language-aware suffix, H1 reinforcement).
- **`docs/mrc/_chapter-index-snippet.zh.md`** and
  **`docs/mrc/_chapter-index-snippet.en.md`** — embeddable Index blockquote
  for use at the top of each MRC doc.

### 2. Per-file changes (12 MRC docs)

- **H1 reinforcement**: every file now starts with
  `# 1.X EN Title / ZH 标题` (e.g. `# 1.4 Field Definitions / 字段定义`).
  H1 was added where missing (10 files) and replaced where pre-existing
  (`toc.{en,zh}.md`).
- **Chapter Index snippet** embedded right after the Purpose / Audience /
  修订历史 blockquote, before the `---` separator, in 10 files (`toc.{en,zh}.md`
  skipped since § 4 + § 9 of TOC already serve the same role).
- **Inline-citation rewrite** — ~280 ref-sites converted from bare numeric
  to three-element form. Examples:
  - ZH: `第 1.4 章` → `1.4 字段定义 (1.4-fields.zh.md)`
  - ZH: `1.5 § 10 政策 5` → `1.5 验证规则 (1.5-rules.zh.md) § 10 政策 5`
  - EN: `chapter 1.3` → `1.3 Sheet Rendering Layer (1.3-sheets.en.md)`
  - EN: `see 1.1` → `see 1.1 Raw Data Layer (1.1-rawdata.en.md)`
- Self-references (same-document `§ 4.1`) intentionally left untouched
  (no chapter-name needed inside the same file).

### 3. Meta-file changes

- `progress.md` — 5 inline rewrites
- `plan.md` — 0 (no MRC chapter references in current plan)
- `test_reports/stage1-mrc-*.md` × 8 — 43 inline rewrites total

## Tooling (kept in `tools/`)

| Script | Purpose |
|---|---|
| `tools/rewrite_xrefs.py` | Pattern-based rewrite for `docs/mrc/*.md`: adds H1, inserts Index snippet, converts old → new form |
| `tools/cleanup_xrefs.py` | Post-pass: collapses accidental `<Title> (file.md) <Title> (file.md)` duplicates and inserts CJK whitespace |
| `tools/rewrite_xrefs_meta.py` | Same rewrite (no H1, no Index) for meta files (`progress.md` / `plan.md` / `test_reports/stage1-mrc-*.md`) |
| `tools/cleanup_xrefs_meta.py` | Cleanup pass for the meta files |

All scripts are idempotent (guard checks prevent double H1 or double Index
insertion).

## Verification

| Check | Result |
|---|---|
| `python tools/stage_doc_checks.py` | **17/17 ALIGN OK** (each MRC doc +1 heading from new H1, symmetric across EN/ZH); Citations **698 PASS / 0 missing / 0 out-of-range** |
| `pytest -q` | **14 passed in 2.61s** |
| `mkdocs build --strict` | No content warnings (only pre-existing Material-for-MkDocs framework banner) |
| Bare-form residue grep (`see 1.X` / `chapter 1.X` / `第 1.X 章` not followed by a title) | **0 hits** in scope (the only remaining occurrences are intentional "old → new" examples inside `_chapter-index.md` and unrelated `1.2.1` / `1.2.2` sub-numbered references to other-servicer chapters in out-of-scope `stage1-carrington_*` / `stage1-shellpoint_*` / `stage1-overall-flow_*` test reports) |
| Duplicate-name grep (`(file.md) <Title> (file.md)`) | **0 hits** |
| Per-file Index count | exactly **1** per doc (idempotent confirmed) |

## Conventions adopted (documented in `_chapter-index.md` § 2)

| Form | Example (ZH) | Example (EN) |
|---|---|---|
| Whole chapter | `1.4 字段定义 (1.4-fields.zh.md)` | `1.4 Field Definitions (1.4-fields.en.md)` |
| Chapter + section | `1.5 验证规则 (1.5-rules.zh.md) § 10 政策 5` | `1.5 Validation Rules (1.5-rules.en.md) § 10` |
| Self-reference | `§ 4.1`（无章节名） | `§ 4.1` (no chapter name) |
| Compact (in tables / mermaid) | `→ 1.4 1.4-fields.zh.md § 10 gap 3` | same |

## Out of scope / known follow-ups

- `1.6 Baseline XLSX Behavior (1.6-baseline.zh.md)` is referenced everywhere
  but the file itself is not yet authored — references will resolve once
  `stage1-mrc-baseline` is executed; no rework needed then.
- `1.2.1` / `1.2.2` etc. (Carrington / Shellpoint sub-chapter numbering)
  in non-MRC test reports were left untouched (different chapter scheme).
- Project has no `git` repository, so no commit was made; this report is
  the canonical change record (mirrors the convention used by
  `stage1-mrc-dataflow-v2-refine_2026-05-17.md` and
  `stage1-mrc-fields-v2-refine_2026-05-17.md`).

## Maintenance contract

Whenever a new MRC chapter is added or renamed:

1. Update `docs/mrc/_chapter-index.md` § 1 (only source of truth).
2. Regenerate `_chapter-index-snippet.{zh,en}.md`.
3. Re-run `tools/rewrite_xrefs.py` + `tools/cleanup_xrefs.py` to propagate.
4. Re-run `tools/stage_doc_checks.py` + `mkdocs build --strict` to verify.
