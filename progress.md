# Progress tracker

> **Purpose**: Single source of truth for "where are we?" and "what's next?" in v9.1.
> **Audience**: next agent / next session / user reviewer.
> Updated at the end of every meaningful session.

> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v4 — full rewrite for **v9.1 MRC-only laser focus + placeholder-everywhere**. Stage 1 collapsed to 8 MRC chapters; non-MRC servicers tracked via `pending-deferred` placeholders only. Stage 2 includes 12 MRC todos covering engine + cell-identity harness + 8-feature UI. |
> | 2026-05-16 | Copilot CLI agent | v3 — full rewrite for v8 Stage 1/2 structure. |
> | 2026-04-30 → 2026-05-16 | Copilot CLI agent | v1 / v2 — v6/v7 bootstrap + MRC pilot tracking (now frozen, see plan v8/v9). |

---

## Current stage

**Stage 2 — design pass (in parallel with closing G2 + G3 baseline gates).**
Stage 1 G1 sign-off recorded 2026-05-17 (provisional, iterative refinement
allowed — see `AGENTS.md` § 6.11). Plan: see session folder `plan.md`
(Stage 2 Readiness Assessment). Status registry: `docs/_status/servicers-registry.{zh,en}.md`.

**Active gates**
- ✅ G1 closed — `stage1-mrc-review` done (provisional sign-off, see `decisions.md` 2026-05-17 entry)
- ⏸ **G2a** open — `mrc-snapshot` (export Redshift inputs to local Parquet/CSV under `baselines/mrc/2026-04-30/input_snapshots/`; needs user with Redshift access). **Redefined 2026-05-17**: G2 no longer means "freeze Redshift"; it means freeze the **input dataset**. See `decisions.md` 2026-05-17 entry + session `plan.md` § 4.2.
- ⏸ **G2b** open — `mrc-source-baseline` + `mrc-gold` (run unmodified legacy MRC code against frozen snapshot via Parquet shim; produce baseline XLSX + manifest; cross-check vs LearningLog gold XLSX). Agent-driven once G2a lands.
- ⏸ G3 open — `stage1-mrc-baseline-verify` (V1–V12 against physical XLSX from G2b)

### G2a Track A progress

| Todo | Status | Output |
|---|---|---|
| **A1** — exhaustive MRC SQL coverage scan | ✅ **done** 2026-05-17 | `tools/freeze_snapshot.py` v2.0; `_export_queries/template/` (21 SQL files); `_export_queries/_coverage.md`; `_plan_index.json` updated |
| **A2** — deep-dive on dynamic SQL / missing patterns | ⏳ pending | tbd (no missing templates found by A1 scanner — confirm before starting) |
| **A3** — placeholder resolver `--resolve` flag | ✅ **done** 2026-05-17 | `tools/freeze_snapshot.py` v2.1; `_export_queries/resolved/` (≥9 SQL files); `_bindings.json`; `tests/tools/test_freeze_resolve.py` |
| **A4** — operator export (Redshift VPN required) | ✅ **done** 2026-05-17 (verify subcommand) | `tools/freeze_snapshot.py verify`; 8 checks C1–C6 core + C7/C8 strict; `tests/tools/test_freeze_verify.py` (16 tests) |
| **A5** — manifest + export orchestration | ⏳ pending | `freeze_snapshot.py export` full implementation |
| **A6** — Redshift dependency catalog | ✅ **done** 2026-05-17 | `docs/mrc/_g2a-redshift-dependencies.{zh,en}.md`; cross-refs in `1.1-rawdata.{zh,en}.md`; `decisions.md` entry |

**Open in parallel right now (design tier, 6 todos `pending`)**: `stage2-mrc-feature-list`, `stage2-mrc-srs`, `stage2-mrc-data-model`, `stage2-mrc-ui-design`, `stage2-mrc-dev-plan`, `stage2-mrc-extensibility-spec`.
**Blocked on G2 + G3 + extensibility-spec (impl tier, 7 todos)**: `stage2-mrc-ingestion`, `stage2-mrc-engine`, `stage2-mrc-xlsx-renderer`, `stage2-mrc-cell-identity-harness`, `stage2-mrc-api`, `stage2-mrc-ui-impl`, `stage2-mrc-acceptance`.

### Servicer status matrix (mirror of `docs/_status/servicers-registry.*`)

| Servicer | Sheets | Stage 1 doc | Stage 2 system |
|---|---|---|---|
| MRC | 5 | ✅ done (provisional, iterative refinement allowed per AGENTS § 6.11) | 🚧 design pass started; impl blocked on G2 + G3 |
| Carrington | 6 | ✅ done (archived under `_archived/pre-mrc-pivot/`) | ⛔ not started |
| Shellpoint | 5 | ✅ done (archived) | ⛔ not started |
| Arvest | 4 | ⏳ placeholder | ⛔ not started |
| CC5 | 2 | ⏳ placeholder | ⛔ not started |
| Selene | 5 | ⏳ placeholder | ⛔ not started |
| SLS | 5 | ⏳ placeholder | ⛔ not started |
| Scattered | n/a | ⏳ placeholder | ⛔ not started |
| Cross-servicer dataflow | n/a | ⏳ placeholder | ⛔ not started |

### Stage 1 progress so far

| Todo | Status | Output | Test report |
|---|---|---|---|
| `stage1-toc` | ✅ done (archived) | `docs/_archived/pre-mrc-pivot/toc.{zh,en}.md` | `test_reports/stage1-toc_2026-05-16.md` |
| `stage1-overall-flow` | ✅ done (archived) | `docs/_archived/pre-mrc-pivot/overall-flow.{zh,en}.md` | `test_reports/stage1-overall-flow_2026-05-16.md` |
| `stage1-carrington` | ✅ done (archived) | `docs/_archived/pre-mrc-pivot/carrington.{zh,en}.md` | `test_reports/stage1-carrington_2026-05-17.md` |
| `stage1-shellpoint` | ✅ done (archived) | `docs/_archived/pre-mrc-pivot/shellpoint.{zh,en}.md` | `test_reports/stage1-shellpoint_2026-05-17.md` |
| `stage1-pending-registry` | ✅ done | `docs/_status/servicers-registry.{zh,en}.md` + 6 `docs/<servicer>/_pending.{zh,en}.md` stubs | `test_reports/stage1-pending-registry_2026-05-17.md` |
| `stage1-mrc-toc` | ✅ done | `docs/mrc/toc.{zh,en}.md` | `test_reports/stage1-mrc-toc_2026-05-17.md` |
| `stage1-mrc-rawdata` | ✅ done | `docs/mrc/rawdata.{zh,en}.md` | `test_reports/stage1-mrc-rawdata_2026-05-17.md` |
| `stage1-mrc-dataflow` | ✅ done | `docs/mrc/dataflow.{zh,en}.md` | `test_reports/stage1-mrc-dataflow_2026-05-17.md` |
| `stage1-mrc-sheets` | ✅ done | `docs/mrc/sheets.{zh,en}.md` | `test_reports/stage1-mrc-sheets_2026-05-17.md` |
| `stage1-mrc-fields` | ✅ done | `docs/mrc/fields.{zh,en}.md` | `test_reports/stage1-mrc-fields_2026-05-17.md` |
| `stage1-mrc-rules` | ✅ done | `docs/mrc/rules.{zh,en}.md` | `test_reports/stage1-mrc-rules_2026-05-17.md` |
| `stage1-mrc-baseline` | ✅ done | `docs/mrc/1.6-baseline.{zh,en}.md` + `baselines/mrc/2026-04-30/` placeholder | `test_reports/stage1-mrc-baseline_2026-05-17.md` |
| `stage1-mrc-review` | ✅ done (G1, provisional sign-off 2026-05-17) | `decisions.md` 2026-05-17 entry + `AGENTS.md` § 6.11 living-docs rule | — |
| `stage1-mrc-baseline-verify` | ⏳ blocked on G2 (G3 owner) | upgrade V1–V12 in 1.6 § 9 to `[CONFIRMED]` against physical XLSX | — |
| `stage1-arvest` / `-cc5` / `-selene` / `-sls` / `-scattered` / `-dataflow` / `-review` | 🕓 pending-deferred (placeholder only) | `docs/<servicer>/_pending.{zh,en}.md` stubs | — |

Stage 2 todos: 12 original `stage2-mrc-*` + 1 new `stage2-mrc-extensibility-spec`. Design tier (6) now `pending`; impl tier (7) blocked on G2 + G3 + extensibility-spec. Plus 9 generic v8 `stage2-*` `pending-deferred` (superseded).

---

## Last session

- **Date**: 2026-05-17
- **Session id**: `4cd52a8e-d034-4def-84a0-04057dd64872` (Copilot CLI, autopilot then interactive)
- **Highlights**:
  1. Delivered `stage1-shellpoint` chapter (5 sheets, zh+en, 12 headings); fixed mermaid node-ID visibility (v1.1: `SH1["SH1 · Shellpoint_Summary_check"]`) across both shellpoint and carrington chapters.
  2. **Plan v8 → v9.1 pivot** triggered by user prompts 37–38: scope narrows to **MRC only**; equivalence bar = **cell-identical XLSX**; Stage 2 includes 8-feature UI; pre-v8 MRC pilot assets un-frozen; placeholder-everywhere rule for un-analyzed servicers.
  3. Created `docs/_status/servicers-registry.{zh,en}.md` (canonical status matrix) + 6 `docs/<servicer>/_pending.{zh,en}.md` stubs (arvest, cc5, selene, sls, scattered, dataflow) wired into `mkdocs.yml` nav under "Project status" and "Pending servicers".
  4. SQL: extended `status` CHECK constraint to add `pending-deferred`; deferred 7 non-MRC stage1-* todos and 9 superseded v8 stage2-* todos to `pending-deferred`; inserted 8 new `stage1-mrc-*` + 12 new `stage2-mrc-*` todos with full dependency graph.
  5. Added AGENTS.md § 6.8 (servicer-state transparency / placeholder rule).
  6. mkdocs --strict ✅ (with new nav); pytest 7/7 ✅; `tools/stage_doc_checks.py` 4 pairs aligned + 260 citations PASS ✅.
  7. **Cleanup C0 executed**: moved 4 polished chapters (toc / overall-flow / carrington / shellpoint, zh+en) from `docs/validation-report-logic/` → `docs/_archived/pre-mrc-pivot/`; removed the empty subdir; archived chapters dropped from mkdocs nav but kept under `stage_doc_checks.py` PAIRS so they can't bit-rot.
  8. **Doc-check tool upgraded**: PAIRS extended to 11 (registry + 6 stubs + 4 archived); `rglob("*.md")` walks all of `docs/`; ROOT fallback added for whitebox-local citations (`whitebox/validators/_placeholder/hello.py`); citation lookup now uses a basename→paths cache pruning `.git/.venv/...` (previously O(citations × repo size), now ms). Final: **11/11 ALIGN OK + 292 citations PASS**.
  9. **`stage1-pending-registry` marked done in SQL**; test report `test_reports/stage1-pending-registry_2026-05-17.md` written.
  10. **Mermaid node-ID legend rule added** (AGENTS.md § 6.9): every dataflow figure that uses short IDs (`T#`, `V#`, `SH#`) must be followed by a legend table mapping each ID to its real source/business name and stating that IDs are display-only cross-references. Applied retroactively to the 4 archived chapters (`shellpoint.{zh,en}.md`, `carrington.{zh,en}.md`). Triggered by user prompt 39 (screenshot showed `SH1`/`SH2`/`V1`/`V2` in prose without a key).
  11. **Cleanup B done** (`cleanup-c6-registry-servicer-status`): new `docs/_status/servicers.yaml` manifest + `tools/schema/servicer.schema.json` JSON schema; `tools/registry.py` extended with `Servicer` dataclass / `load_servicers()` / `Registry.servicers` / 5 cross-checks; `tests/test_registry_servicers.py` with 7 tests; CLI `python tools/registry.py` now prints a "Servicers" section (9 entries, done=2 / in-progress=1 / pending-analysis=6). Test matrix: pytest 14/14 (was 7), stage_doc_checks 11/11 + 292 citations, mkdocs --strict ✅. Test report `test_reports/cleanup-c6_2026-05-17.md`.
  12. **Cleanup A done** (`cleanup-a-plan-convention-refresh`): `plan.md` "Per-chapter conventions" now points at AGENTS § 6.7 / § 6.9; new `plan.md` section "Stage 1 baseline `remit_date`" pins the value to `2026-04-30` with rationale. Matching 3-bullet block appended to `decisions.md` (legend rule, remit_date pin, registry servicer-state). No code change. Test matrix re-run green.
  13. **`stage1-mrc-toc` delivered**: `docs/mrc/toc.{zh,en}.md` (11 H2 sections, heading-aligned, ~108 lines each). Wired into `mkdocs.yml` nav under MRC. `tools/stage_doc_checks.py` PAIRS now 12. Surfaces a **correction**: MRC has **5 validators (incl. `mrc_other_check`)**, not the "4, no mrc_other_check" stated in earlier plan v9.1 drafts — source-verified against `mrc_validation.py:8-158` and `remit_validation.py:134-144`. Propagated to `docs/_status/servicers.yaml` (registry md was already "5"); decisions.md updated. Test matrix: **12/12 ALIGN OK + 320 citations PASS**, pytest **14/14**, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-toc_2026-05-17.md`.
  14. **`stage1-mrc-rawdata` delivered**: `docs/mrc/rawdata.{zh,en}.md` (10 H2 + sub-sections, heading-aligned, 14 headings each). Wired into mkdocs nav under MRC. PAIRS now 13. Source-verified raw-data layer: 13 ingested `mrc.portmrcremit*` tables (sheet → table / sheet → loanid-col / column-rename map), full loader call graph with mermaid + legend, identifies the **5 raw tables actually read by the validators** (4 `mrc.*` + 2 `port.*`), and resolves the concrete `fctrdt` value at baseline: **`fctrdt = 2026-05-01`**, **`fctrdt_1m = 2026-04-01`** — closing the chapter-1.0 known-unknown. Records 6 explicit assumptions / gaps for 1.2 / 1.4 / 1.6. Test matrix: **13/13 ALIGN OK + 412 citations PASS**, pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-rawdata_2026-05-17.md`.
  15. **`stage1-mrc-dataflow` delivered**: `docs/mrc/dataflow.{zh,en}.md` (9 H2 + sub-sections, heading-aligned, 19 headings each). Wired into nav; PAIRS now 14. Full structural unpack of both SQL templates (`mrc_adv_validation` 50 lines, `mrc_general_check` 71 lines): CTE list, join topology, emitted column catalog (25 + 27+ columns), parameter substitution table; plus inline-SQL summaries for the other 3 validators (`mrc_summary_check` aggregate; `mrc_service_fee_check` 3-way join; `_mrc_adv_info_sql`+`mrc_other_check` 3-way UNION ALL with pandas-side MoM merge). Two mermaid figures with caption + legend per § 6.9: Figure 1.2.3 (overall dataflow flowchart, 13 nodes incl. all source tables) and Figure 1.2.7 (per-`remit_date` validator-to-sheet sequence diagram with step-by-step explanation). Includes the **§ 7.1 validator→key→sheet contract table** — the cell-identity boundary Stage 2 must reproduce. Notes the **CTE-naming asymmetry** (`p1/p2` vs `p/p2` mean opposite anchors in the two templates) as documented-but-not-fixed. Test matrix: **14/14 ALIGN OK + 494 citations PASS**, pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-dataflow_2026-05-17.md`.
  16. **Project rule `AGENTS.md` § 6.10 + user rule § 7 added — "diagram + text co-requirement"**: every workflow / dataflow / ETL / validation flow / system-interaction doc must include both a diagram and a 5-bullet textual explanation (business purpose · execution flow · input/output · key transformations · dependencies/assumptions); complex logic requires an overview diagram plus decomposed sub-process diagrams. Project rule wired into the end-of-stage P0 gate; user rule overridable per-project. Triggered by user prompt this session.
  17. **`stage1-mrc-dataflow` v2 refine (apply § 6.10)**: same files `docs/mrc/dataflow.{zh,en}.md`. Added 5-bullet explanation block under Figure 1.2.3; added 5 decomposed per-validator sub-flow diagrams (**Figures 1.2.4 — `mrc_check_adv_balance`**, **1.2.5 — `mrc_check_general_info`**, **1.2.6 — `mrc_summary_check`**, **1.2.7 — `mrc_service_fee_check`**, **1.2.8 — `mrc_other_check`**), each with its own 5-bullet block and source citation. Renumbered the existing validator-to-sheet sequence diagram **1.2.7 → 1.2.9** to avoid clash with the new V4 diagram, and added its own 5-bullet block. No new H2/H3 — heading count remains 19. Test matrix: **14/14 ALIGN OK + 510 citations PASS** (+16 vs v1), pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-dataflow-v2-refine_2026-05-17.md`.
  18. **`stage1-mrc-sheets` delivered**: `docs/mrc/sheets.{zh,en}.md` (11 H2 + 14 H3 = 25 headings each, ~33 KB). Wired into mkdocs nav under MRC (`- 1.3 Sheets`); PAIRS now 15. Per-sheet rendering layer fully documented: 5 column-list helpers (`_summary_columns` 14 cols / `_general_columns` 35 cols, 7 highlights / `_advance_columns` 27 cols, 4 highlights / `_service_fee_columns` 8 cols, 1 highlight / `_adv_info_columns` 7 cols), shared rendering machinery (`_validation_report_col` / `_validation_report_sheet` / `sheet_df_round` / `data_type_format` / `header_format` / `diff_cell_format`), and 5 sheet-registry entries (`:1327-1356`). 5 figures with 5-bullet text per § 6.10: 1.3.3 overall pipeline + 1.3.4 highlight cascade + 1.3.5–1.3.9 per-sheet structure. Surfaces 6 gaps for chapters 1.4/1.5/1.6 (e.g. `pandi_diff_remitvsdaily` non-highlighted vs `pandi_schedule_diff_remitvsdaily` highlighted; `nextduedate_diff` typed `float` with `round_to=2` despite day-count semantics; `±inf`/`NaN` cell rendering for `amt_MoM` undefined). Test matrix: **15/15 ALIGN OK + 562 citations PASS** (+52), pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-sheets_2026-05-17.md`.
  19. **`stage1-mrc-fields` delivered**: `docs/mrc/fields.{zh,en}.md` (11 H2 + 15 H3 = 26 headings each; EN ~45 KB, ZH ~36 KB). Wired into mkdocs nav (`- 1.4 Fields`); PAIRS now 16. Per-column lineage tables for **91 output columns** across the 5 MRC sheets (Summary 14 + General 35 + Advance 27 + ServiceFee 8 + AdvInfo 7), each row documenting: source `table.column`, transform expression (with literal SQL line citation), type / round, NULL handling / edge cases. Sources reverse-engineered from `mrc_validation.py:8-158` and `servicer_validation_with_portdaily.py:583-705`. 6 figures with 5-bullet text per § 6.10: 1.4.3 5-layer overall lineage + 1.4.4–1.4.8 per-sheet lineage diagrams. Surfaces **3 new field-level gaps** (V2/V3 CTE-alias overlap; **addition** sign convention on Advance diff cols; `totalservicefee` SUM-of-add vs SUM-then-add nuance) on top of 1.3 Sheet 渲染层 (1.3-sheets.zh.md)'s 6 gaps — total 9 documented gaps for chapters 1.5/1.6. Includes cross-sheet field reuse table (`port.portmonth` columns feeding multiple sheets) for Stage 2 contract. Test matrix: **16/16 ALIGN OK + 614 citations PASS** (+52), pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-fields_2026-05-17.md`.
  20. **`stage1-mrc-rules` delivered**: `docs/mrc/rules.{zh,en}.md` (11 H2 + 18 H3 = 29 headings each; EN ~35 KB, ZH ~25 KB). Wired into mkdocs nav (`- 1.5 Rules`); PAIRS now 17. Lifts the 3 implicit "rule" layers of the existing MRC path into one catalog: (a) SQL projection layer `case-when NULL` guards; (b) render layer `pd.to_numeric.abs() > threshold=0` (strict `>`); (c) validator layer `try/except → return None` → `MISSING-SHEET`. Introduces a 6-label severity vocabulary (`HIGHLIGHT` / `SUPPRESSED` / `NO-HIGHLIGHT` / `INFO` / `MISSING-SHEET` / `OPEN-POLICY`) used only within chapters 1.5–1.7. Per-validator rule catalogs: V1 has 2 rules (sheet existence + sum-order); V2 has 12 rules (5 highlight + 3 NULL guards + 1 NO-HIGHLIGHT + 1 binary indicator + 1 sheet existence + 1 silent-fallback); V3 has 6 rules (4 highlight on additive diffs + 1 NULL guard + 1 sheet existence); V4 has 4 rules (1 highlight + silent NULL-miss + sheet existence + fctrdt/asofdate duplication); V5 has 6 rules (sheet existence + 4 NaN/inf branches + non-deterministic row order). 5 figures with 5-bullet text per § 6.10: 1.5.3 overall rule application + 1.5.4–1.5.8 per-validator decision trees. § 9 documents cross-validator failure semantics — Prefect never sees an MRC validator fail; the email composer treats highlighted ≡ clean workbooks identically. § 10 hands 1.7 用户走读评审 **9 explicit `OPEN-POLICY` questions** with `[PROPOSED]` defaults (e.g. should `MISSING-SHEET` raise P0; should `pandi_diff_remitvsdaily` join the highlight list; should V5 sort deterministically). Test matrix: **17/17 ALIGN OK + 696 citations PASS** (+82), pytest 14/14, mkdocs --strict ✅. Test report `test_reports/stage1-mrc-rules_2026-05-17.md`.

### Previous session (2026-05-16)

  1. Approved plan v8 (strict 2-stage separation); migrated SQL todos and froze pre-v8 assets.
  2. Produced `stage1-toc` deliverable (split bilingual `.zh.md` + `.en.md`).
  3. Produced `stage1-overall-flow` deliverable; later expanded § 1.1.7 into 6 inline workflow / dataflow diagrams.
  4. Added project rule **AGENTS.md § 6.5–§ 6.7**: end-of-stage automated test + report, test-report directory, doc header + inline diagram rule.
  5. Built `tools/stage_doc_checks.py`.

---

## Next concrete action

For the next agent (or me, next turn):

1. Read `AGENTS.md` → this `progress.md` → `plan.md` v9.1 → tail of `prompts.md` → tail of `decisions.md` → `docs/_status/servicers-registry.zh.md`.
2. Read `docs/mrc/toc.zh.md` (chapter map) for orientation.
3. Start `stage1-mrc-baseline` (1.6 Baseline XLSX 行为 (1.6-baseline.zh.md)): capture the 2026-04-30 validation report XLSX baseline interpreted through chapters 1.3 (rendering) and 1.5 (rule taxonomy); store gold XLSX under `baselines/mrc/2026-04-30/validation_report.xlsx`; write `docs/mrc/baseline.{zh,en}.md` documenting per-sheet observed cell state, count of `HIGHLIGHT` / `SUPPRESSED` / `MISSING-SHEET` outcomes, and per-tab notes for 1.7 用户走读评审 reviewer. Note: may require runtime data access (Redshift VPN + Vault token via `PrefectFlow-LearningLog/scripts/run_remit_validation.py` wrapper); if blocked, document the blocker and pivot to `stage1-mrc-review` 1.7 用户走读评审 with the 9 `OPEN-POLICY` questions already on the table.
4. Run the test matrix after the chapter; per AGENTS.md § 6.5.

---

## Pre-v9.1 history (summarized; full detail in checkpoints)

- **2026-04-25 → 2026-04-30**: Phase 0 bootstrap — frozen.
- **2026-04-30 → 2026-05-12**: Phase 1 — registry / sqlglot lineage / freeze_snapshot / diff_report / autodoc — **frozen** at v8; **un-frozen for Stage 2 use at v9.1**.
- **2026-05-12 → 2026-05-15**: Phase 1.5 self-test + Phase 2 MRC pilot start (scope.md, sheets/MRC_*.yaml, gold JSONs) — **frozen** at v8; **un-frozen as Stage 2 inputs at v9.1**.
- **2026-05-16 → 2026-05-17 (v8)**: doc-first 2-stage; delivered toc / overall-flow / carrington / shellpoint chapters with bilingual zh/en + test matrix. To be archived under `docs/_archived/pre-mrc-pivot/` in cleanup C0.
- **2026-05-17 (v9 → v9.1)**: scope narrowed to MRC; placeholder-everywhere rule activated.

For full per-checkpoint history see
`C:\Users\jli\.copilot\session-state\4cd52a8e-d034-4def-84a0-04057dd64872\checkpoints\`.
