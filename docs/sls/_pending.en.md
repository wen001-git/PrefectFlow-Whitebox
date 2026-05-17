# SLS — Pending analysis placeholder (en)

> **Status**: ⏳ pending-deferred (v9.1 placeholder).
> **Purpose**: placeholder doc. SLS's Validation Report generation logic
> has **not** yet been analyzed. This file guarantees the mkdocs nav and the
> servicers-registry both reserve a slot for SLS so it is not forgotten;
> when analysis happens, this file will be replaced by the toc / rawdata /
> dataflow / sheets / fields / rules chapter set.
>
> **Intended audience**: the future session agent picking up SLS +
> the user.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — created (v9.1 placeholder-everywhere rule). |

---

## Summary

- **Estimated sheets**: 5 (assumed)
- **Known source files** (in `flow/remit_validation/`):
  sls_db.py, sls_gen_portremit.py, sls_validation.py
- **Current state**: not analyzed.

---

## Open questions

1. How many @task validators does SLS have? What are their names?
2. Which sheets does each validator write to? What are the sheet names?
3. What are the column layouts, header rows, and highlight rules per sheet? (see `util/gen_remit_validation_report.py`)
4. Which SQL templates from `servicer_validation_with_portdaily.py` are reused? (shared with carrington / shellpoint / mrc?)
5. What is the `servicer` field value in `port.portmonth` for SLS?
6. Is there a SLS-specific schema (e.g. `sls.*`) serving as the unified layer?
7. Any known defects or edge cases?

---

## Assumptions (to be verified)

- Reuses the 4-dimension organization established by carrington/shellpoint/mrc (overview / per-sheet / per-field / dataflow branch).
- Follows v8 doc conventions (doc-header, zh/en alignment, `file.py:LINE` citations, inline mermaid with caption + numbered steps).
- Follows the v9.1 mermaid-node-ID-prefix convention (`SH1["SH1 · ..."]`).

---

## Follow-up when analyzed

1. Create `docs/sls/toc.{zh,en}.md`, `rawdata.{zh,en}.md`, `dataflow.{zh,en}.md`, `sheets.{zh,en}.md`, `fields.{zh,en}.md`, `rules.{zh,en}.md` mirroring the MRC chapter template.
2. Update `mkdocs.yml` nav: move SLS from "Pending servicers" to the active chapter section.
3. Add the new doc pairs to `tools/stage_doc_checks.py` PAIRS.
4. Update `docs/_status/servicers-registry.{zh,en}.md` + `plan.md` status matrix: ⏳ → ✅.
5. Write a test report under `test_reports/`.
6. Move the SQL todo (`stage1-sls` or the further-split `stage1-sls-*`) from `pending-deferred` → `done`.

See plan.md "Placeholder reservation policy" and AGENTS.md §§ 6.5–6.8.

---

## Notes

KNOWN ISSUE: 2026-04 empty-data bug must be documented when analyzed. sls_gen_portremit.py is unique to SLS — document its role.
