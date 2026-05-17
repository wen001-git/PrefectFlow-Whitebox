# Cross-servicer dataflow / lineage — Pending analysis placeholder (en)

> **Status**: ⏳ pending-deferred (v9.1 placeholder).
> **Purpose**: placeholder doc. Cross-servicer dataflow / lineage's Validation Report generation logic
> has **not** yet been analyzed. This file guarantees the mkdocs nav and the
> servicers-registry both reserve a slot for Cross-servicer dataflow / lineage so it is not forgotten;
> when analysis happens, this file will be replaced by the toc / rawdata /
> dataflow / sheets / fields / rules chapter set.
>
> **Intended audience**: the future session agent picking up Cross-servicer dataflow / lineage +
> the user.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — created (v9.1 placeholder-everywhere rule). |

---

## Summary

- **Estimated sheets**: n/a
- **Known source files** (in `flow/remit_validation/`):
  (synthesis chapter — pulls from all per-servicer chapters)
- **Current state**: not analyzed.

---

## Open questions

1. How many @task validators does Cross-servicer dataflow / lineage have? What are their names?
2. Which sheets does each validator write to? What are the sheet names?
3. What are the column layouts, header rows, and highlight rules per sheet? (see `util/gen_remit_validation_report.py`)
4. Which SQL templates from `servicer_validation_with_portdaily.py` are reused? (shared with carrington / shellpoint / mrc?)
5. What is the `servicer` field value in `port.portmonth` for Cross-servicer dataflow / lineage?
6. Is there a Cross-servicer dataflow / lineage-specific schema (e.g. `dataflow.*`) serving as the unified layer?
7. Any known defects or edge cases?

---

## Assumptions (to be verified)

- Reuses the 4-dimension organization established by carrington/shellpoint/mrc (overview / per-sheet / per-field / dataflow branch).
- Follows v8 doc conventions (doc-header, zh/en alignment, `file.py:LINE` citations, inline mermaid with caption + numbered steps).
- Follows the v9.1 mermaid-node-ID-prefix convention (`SH1["SH1 · ..."]`).

---

## Follow-up when analyzed

1. Create `docs/dataflow/toc.{zh,en}.md`, `rawdata.{zh,en}.md`, `dataflow.{zh,en}.md`, `sheets.{zh,en}.md`, `fields.{zh,en}.md`, `rules.{zh,en}.md` mirroring the MRC chapter template.
2. Update `mkdocs.yml` nav: move Cross-servicer dataflow / lineage from "Pending servicers" to the active chapter section.
3. Add the new doc pairs to `tools/stage_doc_checks.py` PAIRS.
4. Update `docs/_status/servicers-registry.{zh,en}.md` + `plan.md` status matrix: ⏳ → ✅.
5. Write a test report under `test_reports/`.
6. Move the SQL todo (`stage1-dataflow` or the further-split `stage1-dataflow-*`) from `pending-deferred` → `done`.

See plan.md "Placeholder reservation policy" and AGENTS.md §§ 6.5–6.8.

---

## Notes

Requires per-servicer docs complete first. Output: full lineage map raw vendor file -> raw schema table -> unified Redshift table -> validation query -> sheet.
