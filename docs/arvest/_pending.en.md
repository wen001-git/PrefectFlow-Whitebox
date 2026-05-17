# Arvest — Pending analysis placeholder (en)

> **Status**: ⏳ pending-deferred (v9.1 placeholder).
> **Purpose**: placeholder doc. Arvest's Validation Report generation logic
> has **not** yet been analyzed. This file guarantees the mkdocs nav and the
> servicers-registry both reserve a slot for Arvest so it is not forgotten;
> when analysis happens, this file will be replaced by the toc / rawdata /
> dataflow / sheets / fields / rules chapter set.
>
> **Intended audience**: the future session agent picking up Arvest +
> the user.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — created (v9.1 placeholder-everywhere rule). |

---

## Summary

- **Estimated sheets**: 4 (assumed)
- **Known source files** (in `flow/remit_validation/`):
  arvest_db.py, arvest_validation.py
- **Current state**: not analyzed.

---

## Open questions

1. How many @task validators does Arvest have? What are their names?
2. Which sheets does each validator write to? What are the sheet names?
3. What are the column layouts, header rows, and highlight rules per sheet? (see `util/gen_remit_validation_report.py`)
4. Which SQL templates from `servicer_validation_with_portdaily.py` are reused? (shared with carrington / shellpoint / mrc?)
5. What is the `servicer` field value in `port.portmonth` for Arvest?
6. Is there a Arvest-specific schema (e.g. `arvest.*`) serving as the unified layer?
7. Any known defects or edge cases?

---

## Assumptions (to be verified)

- Reuses the 4-dimension organization established by carrington/shellpoint/mrc (overview / per-sheet / per-field / dataflow branch).
- Follows v8 doc conventions (doc-header, zh/en alignment, `file.py:LINE` citations, inline mermaid with caption + numbered steps).
- Follows the v9.1 mermaid-node-ID-prefix convention (`SH1["SH1 · ..."]`).

---

## Follow-up when analyzed

1. Create `docs/arvest/toc.{zh,en}.md`, `rawdata.{zh,en}.md`, `dataflow.{zh,en}.md`, `sheets.{zh,en}.md`, `fields.{zh,en}.md`, `rules.{zh,en}.md` mirroring the MRC chapter template.
2. Update `mkdocs.yml` nav: move Arvest from "Pending servicers" to the active chapter section.
3. Add the new doc pairs to `tools/stage_doc_checks.py` PAIRS.
4. Update `docs/_status/servicers-registry.{zh,en}.md` + `plan.md` status matrix: ⏳ → ✅.
5. Write a test report under `test_reports/`.
6. Move the SQL todo (`stage1-arvest` or the further-split `stage1-arvest-*`) from `pending-deferred` → `done`.

See plan.md "Placeholder reservation policy" and AGENTS.md §§ 6.5–6.8.

---

## Notes

Sheet count assumed 4; verify against arvest_validation.py validator count. SQL templates likely shared via servicer_validation_with_portdaily.py — verify which.
