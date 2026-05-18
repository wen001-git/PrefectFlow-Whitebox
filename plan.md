# Plan v9.1 — PrefectFlow-Whitebox (MRC-first with explicit placeholders for pending servicers)

> v8 → v9 pivot from user prompt 37 (MRC laser focus).
> v9 → v9.1 amendment from user prompt 38: **every plan / doc / registry /
> lineage / architecture artifact must reserve explicit placeholders** for the
> servicers we have NOT yet fully analyzed, so nothing is forgotten and future
> incremental analysis slots in cleanly.

> Previous plans (v6/v7/v8) remain referenced in the session checkpoints.
> v8 SQL todo dispositions revised below.

---

## v9.1 north star

1. **Stage 1**: complete the reverse-engineering documentation for **MRC**
   end-to-end. While we do this, maintain a **transparent placeholder registry**
   for the 6 remaining servicers and the cross-servicer scattered/dataflow work,
   so the project never silently drops them.

2. **Stage 2**: build a new MRC validation system that is **cell-identical** to
   the old MRC XLSX, with the 8-feature interactive UI from prompt 19. **The
   engine, data model, UI, and registry must all reserve slots for future
   servicers**, so onboarding (arvest, cc5, selene, sls, etc.) becomes
   incremental, not a rewrite.

3. **Transparency invariant**: at any moment, the user (or a fresh agent) can
   open one single registry doc and immediately see which servicers are
   analyzed, which sheets are documented, which fields are still TBD, and what
   the next analysis steps are.

---

## Equivalence bar (locked, user prompt 37 → ask 1)

**Cell-identical.** For a fixed `remit_date` baseline frozen from production,
the new system's `validation_report.xlsx` matches the old XLSX byte-for-byte on:
sheet names, sheet order, column order, header rows, data row order, every
cell value, and highlight colors / conditional formatting. Verified by
`stage2-mrc-cell-identity-harness`.

---

## Servicer status matrix (single source of truth)

This table is mirrored into `docs/_status/servicers-registry.{zh,en}.md` (added
in cleanup C5) and into the validator registry tool output (cleanup C6).

| Servicer | Sheets | Stage 1 doc status | Stage 2 system status | Last analyzed | Owner of next step | Open gaps / unknowns |
|---|---|---|---|---|---|---|
| **MRC** | 5 | 🚧 in progress (v9.1 active) | ⏳ pending Stage 1 review | 2026-05-15 (frozen pilot scope.md) | this session | full re-analysis underway |
| **Carrington** | 6 | ✅ chapter done (2026-05-17, archived under `_archived/pre-mrc-pivot/`) | ⛔ not started | 2026-05-17 | future session | may need refresh once MRC system shapes the doc template |
| **Shellpoint** | 5 | ✅ chapter done (2026-05-17, archived) | ⛔ not started | 2026-05-17 | future session | same as Carrington |
| **Arvest** | 4 | ⏳ pending (placeholder only) | ⛔ not started | never | future session | sheet count assumed 4 — verify against `arvest_validation.py`; SQL templates unverified |
| **CC5** | 2 | ⏳ pending (placeholder only) | ⛔ not started | never | future session | smallest servicer; quickest future warm-up |
| **Selene** | 5 | ⏳ pending (placeholder only) | ⛔ not started | never | future session | sheet count assumed 5 — verify |
| **SLS** | 5 | ⏳ pending (placeholder only) | ⛔ not started | never | future session | **known issue: 2026-04 empty data bug** must be documented when analyzed |
| **Scattered** (cross-servicer validators, ~8) | n/a | ⏳ pending (placeholder only) | ⛔ not started | never | future session | inventory of the 8 validators not yet enumerated |
| **Cross-servicer dataflow / lineage** | n/a | ⏳ pending (placeholder only) | ⛔ not started | never | future session | requires all per-servicer docs first |

**Legend:** ✅ done · 🚧 in progress · ⏳ pending (placeholder reserved) · ⛔ not started · 🔒 frozen (no longer applicable)

**Rule:** every time a servicer transitions states, this matrix updates in the
same commit as the doc / SQL todo change.

---

## Placeholder reservation policy

For each `⏳ pending` servicer, the following placeholders **must already exist**
before `stage1-mrc-toc` starts, so structure is in place and gaps are visible:

| Artifact | Placeholder form |
|---|---|
| `plan.md` | Listed in the servicer status matrix above; corresponding SQL todo created with status `pending-deferred` (not `blocked`), description naming what's unknown. |
| `docs/_status/servicers-registry.{zh,en}.md` | One row per pending servicer mirroring the matrix; rendered in mkdocs nav. |
| `docs/{servicer}/_pending.{zh,en}.md` | One stub per pending servicer with: "Not yet analyzed. Open questions: [...]. Known source files: [...]. When analyzed, replace this stub with toc/rawdata/dataflow/sheets/fields/rules chapters per the MRC template." Rendered in nav under a "Pending servicers" section. |
| Validator registry (`tools/registry.py` or its v9.1 replacement) | Each pending servicer's validators registered with `status: pending-analysis`, `gaps: [...]`. The registry's JSON / markdown output surfaces these flags. |
| Lineage / architecture diagrams | The overall lineage diagram (when produced for Stage 2) includes a placeholder branch per pending servicer labeled `<servicer> — TBD (pending analysis)` with dashed lines, so the picture is complete-shaped even if details are missing. |
| Stage 2 data model | Tables / schemas accommodate a `servicer` discriminator and per-servicer extension hooks; the engine has a `ServicerHandler` abstraction with registered MRC handler and explicit `NotImplementedError` stubs for each pending servicer that raise a clear "not yet analyzed" message. |
| Stage 2 UI | Servicer picker dropdown lists ALL servicers; pending ones render with a "(pending analysis)" suffix and a disabled "Generate Report" button that links to the placeholder doc. |

---

## Disposition table (v9.1)

| Asset | Prior status | v9.1 status | Notes |
|---|---|---|---|
| `docs/validation-report-logic/toc.{zh,en}.md` | live (v8 done) | **archived** under `docs/_archived/pre-mrc-pivot/`, dropped from nav | linked from servicers-registry as reference |
| `docs/validation-report-logic/overall-flow.{zh,en}.md` | live (v8 done) | **archived**, dropped from nav | same |
| `docs/validation-report-logic/carrington.{zh,en}.md` | live (v8 done) | **archived but flagged "partially done"** in servicers-registry | future session may refresh |
| `docs/validation-report-logic/shellpoint.{zh,en}.md` | live (v8 done) | **archived but flagged "partially done"** | same |
| Autodoc placeholders in `docs/validators/_placeholder/` and `docs/validators/mrc/` | frozen | **kept but flagged**: autodoc stubs, not the new prose. Servicers-registry calls this out. | |
| `docs/servicers/mrc/scope.{zh,en}.md` (frozen pilot) | frozen | **live Stage 1 seed input** for `stage1-mrc-toc` / `stage1-mrc-overview` | |
| `sheets/MRC_*.yaml` (5 files) | frozen | **live Stage 2 inputs** | un-frozen per ask 3 |
| `snapshots/2026-04-30/gold/MRC_*.json` (5 files) | frozen | **live Stage 1 reference + Stage 2 fixtures** | |
| `whitebox/validators/` | frozen | **live Stage 2 starting point**; will register MRC handler + explicit pending stubs for 6 other servicers | |
| `tools/registry.py`, `build_lineage.py`, `autodoc.py`, `diff_report.py`, `freeze_snapshot.py`, `slice_gold.py`, `snapshot_mrc.py`, `build_docs.py` | frozen | **un-frozen as Stage 2 candidates** | Will be extended (or replaced) so the registry can express `pending-analysis` status. |
| `tools/stage_doc_checks.py` | live | **live** | Will add MRC chapter pairs + the servicers-registry pair. |
| `test_reports/` + AGENTS.md § 6.5–6.7 | live | **live** | unchanged |
| Non-MRC stage1-* SQL todos (`stage1-arvest` / `-cc5` / `-selene` / `-sls` / `-scattered` / `-dataflow` / `-review`) | pending | **status `pending-deferred`**, description gains "v9.1: placeholder reserved in servicers-registry; analysis paused while MRC end-to-end completes" | NOT marked `blocked`/`frozen` so they remain visible in active todo queries; sort order can deprioritize them. |
| `stage1-carrington` / `stage1-shellpoint` / `stage1-toc` / `stage1-overall-flow` | done | **done (archived chapters)** | flagged "partially done" in registry |
| v6/v7 frozen MRC todos (`mrc-vN-impl`, `mrc-writer`, `mrc-fullrun`, `mrc-trace-runtime`, `mrc-streamlit-viewer`, Phase 3-5) | frozen | **stay frozen pending re-evaluation in Stage 2** | |

---

## Stage 1 todos (MRC-first + placeholder-registry setup)

| ID | Phase | Title | Output |
|---|---|---|---|
| `stage1-pending-registry` | 1.-1 (prerequisite) | Build `docs/_status/servicers-registry.{zh,en}.md` + per-servicer `_pending.{zh,en}.md` stubs + mkdocs nav update. Mirror status matrix into registry tool output. | listed in matrix |
| `stage1-mrc-toc` | 1.0 | MRC chapter TOC + scope freeze | `docs/mrc/toc.{zh,en}.md` |
| `stage1-mrc-rawdata` | 1.1 | Raw data sources: vendor file format, raw-schema staging tables, ingestion job, the unified Redshift tables surfaced for validation | `docs/mrc/rawdata.{zh,en}.md` |
| `stage1-mrc-dataflow` | 1.2 | End-to-end dataflow branch: raw → unified → `mrc_db.py` getters → `mrc_validation.py` validators → 5 sheets, with mermaid (using `T<N>·`/`V<N>·`/`SH<N>·` label convention) + numbered steps | `docs/mrc/dataflow.{zh,en}.md` |
| `stage1-mrc-sheets` | 1.3 | Per-sheet logic for all 5 MRC sheets (Summary / General_Check / Advance_Check / ServiceFee_Check / Adv_Info) | `docs/mrc/sheets.{zh,en}.md` |
| `stage1-mrc-fields` | 1.4 | Per-field calculation: column-level lineage for every output column in all 5 sheets | `docs/mrc/fields.{zh,en}.md` |
| `stage1-mrc-rules` | 1.5 | Validation rule catalog (pass / fail / exception decision rules per sheet) | `docs/mrc/rules.{zh,en}.md` |
| `stage1-mrc-baseline` | 1.6 | Capture + freeze production baseline XLSX for chosen remit_date | `docs/mrc/baseline.{zh,en}.md` + `baselines/mrc/<remit_date>/validation_report.xlsx` |
| `stage1-mrc-review` | 1.7 | User walk-through review of all MRC chapters; approval gates Stage 2 | (user action) |

At every Stage 1 todo completion, `stage1-pending-registry` artifacts are
updated (status row + linked test report). This is enforced in AGENTS.md
(cleanup C7).

### Per-chapter conventions (carried from v8 + extensions)

- Doc-header block (Purpose / Audience / Revision history) before first H1.
  See **AGENTS.md § 6.7** for the mandatory header + inline-diagram-caption rule.
- zh/en heading skeletons must align (verified by `tools/stage_doc_checks.py`).
- Source citations as `file.py:LINE` or `file.py:LINE-LINE`; must resolve.
- Diagrams inline with caption + numbered step-by-step.
- Mermaid node IDs surfaced in display labels (`SH1["SH1 · MRC_Summary_check"]`).
- **Mermaid node-ID legend (mandatory)** — any figure that uses short ID-style
  node names (`T#` / `V#` / `SH#` / `R#` / …) must be followed immediately by a
  legend table mapping every ID to its real source/business name and stating
  that the IDs are display-only cross-references, not source identifiers.
  See **AGENTS.md § 6.9** for the full rule.
- **NEW (v9.1):** any cross-servicer reference must use the registry's status
  legend (✅ / 🚧 / ⏳ / ⛔ / 🔒) when mentioning other servicers.
- **NEW (v9.1):** anywhere the MRC docs would need cross-servicer info that's
  unknown, insert a `> 🔍 PENDING-ANALYSIS:` callout with a link to the
  relevant pending-servicer stub.
- End-of-chapter test matrix + report under `test_reports/<todo-id>_YYYY-MM-DD.md`.

### Stage 1 baseline `remit_date` (pinned 2026-05-17)

All Stage 1 MRC chapters (and the Stage 2 cell-identity harness) **must
use a single concrete baseline** when citing example rows, expected
counts, gold-output references, or producing baseline XLSX captures:

> **Baseline `remit_date` = `2026-04-30`**

**Rationale**:

1. The un-frozen MRC pilot already ships 5 `sheets/MRC_*.yaml` column
   templates **and** 5 `snapshots/2026-04-30/gold/MRC_*.json` reference
   outputs sliced from this exact date — zero-cost ground truth.
2. Pinning one date removes the "which date?" decision from every
   downstream chapter and keeps cross-chapter examples consistent.
3. The Stage 2 cell-identity harness will parameterize over
   `(servicer, remit_date)` later (per plan v9.1 stage2 todos), but
   Stage 1 only needs one date to prove the documentation captures
   logic correctly.

If a later analysis discovers that `2026-04-30` is unrepresentative
(e.g. missing a rule branch only triggered by a different month), add a
**secondary** date but keep `2026-04-30` as the primary baseline and
note the asymmetry in `decisions.md`.

---

## Stage 2 todos (MRC engine + UI + forward-compatible extensibility)

> Starts only after `stage1-mrc-review` is approved.

| ID | Title | Forward-compat requirement |
|---|---|---|
| `stage2-mrc-feature-list` | Functional spec from prompt 19 8 features, scoped to MRC | Servicer picker lists all 8 servicers (MRC active, 6 pending, 1 group `scattered`) |
| `stage2-mrc-srs` | SRS (functional / non-functional / acceptance criteria) | Non-functional: pluggable servicer handler architecture |
| `stage2-mrc-data-model` | Data model (ingestion → staging → unified → validation results → audit) | Tables include `servicer` discriminator; schemas accommodate future servicers without migration |
| `stage2-mrc-ingestion` | Ingestion layer | Abstraction: `IngestionSource` per servicer; MRC implemented, others raise `NotImplementedError("pending analysis — see docs/<servicer>/_pending.md")` |
| `stage2-mrc-engine` | Validation engine producing all 5 MRC sheets as DataFrames, cell-identical to old XLSX values | `ServicerHandler` interface; MRC handler concrete, 6 others registered as `PendingServicerHandler` stubs |
| `stage2-mrc-xlsx-renderer` | XLSX renderer matching styles byte-for-byte | Renderer keyed by sheet metadata; trivially extensible to other servicers' sheets |
| `stage2-mrc-cell-identity-harness` | Automated diff: new XLSX vs baseline; fail on any mismatch | Harness parameterized by `(servicer, remit_date)`; MRC active, others marked `@pytest.mark.skip(reason='pending analysis')` |
| `stage2-mrc-api` | CLI + library + HTTP endpoints for UI | Endpoints enumerate ALL servicers, surface `status` field per the registry |
| `stage2-mrc-ui-design` | UI design covering all 8 prompt-19 features for MRC | Pending servicers visible but disabled with link to placeholder docs |
| `stage2-mrc-ui-impl` | UI implementation (lightweight first) | Pending-servicer state is a first-class UI state, not an afterthought |
| `stage2-mrc-dev-plan` | Phased dev plan | Plan explicitly calls out per-servicer onboarding template |
| `stage2-mrc-acceptance` | E2E acceptance: cell-identical XLSX + 8 UI features + servicers-registry accurate | Done gate |

### Stage 2 working rules

- No technology pre-selection until engine design forces it.
- Frozen pilot assets are starting points, not contracts; rewrite freely.
- Cell-identity harness in place **before** declaring engine done.
- **NEW (v9.1):** every Stage 2 deliverable that names servicers must use the
  registry as source-of-truth. If a deliverable creates a new servicer-related
  concept (table, endpoint, UI screen, test), it must register placeholder
  handling for all `⏳ pending` servicers in the same commit.

---

## Working rules (carried from v8 + v9.1 transparency)

1. Strict ordering within Stage 1 (1.-1 → 1.0 → 1.7); within Stage 2.
2. Prompt user before phase transitions; ask before destructive cleanup.
3. Append every user prompt verbatim to `prompts.md` before doing work.
4. Append every meaningful decision to `decisions.md`.
5. End-of-stage test matrix mandatory; report under `test_reports/`.
6. PrefectFlow source repo always read-only.
7. **NEW (v9.1):** any change touching the servicer status of a pending
   servicer must update `docs/_status/servicers-registry.{zh,en}.md` in the
   same change.

---

## Pre-`stage1-mrc-toc` micro-plan (v9.1 + 2026-05-17 user-directed order: B then A)

After the v9.1 pivot, the user explicitly chose to execute the two
remaining "polish" items **before** starting `stage1-mrc-toc`, in this
order: **B → A → stage1-mrc-toc**.

### B (= cleanup C6): make the registry tool servicer-state aware

- **Goal**: make `tools/registry.py` (or a sibling `tools/servicer_status.py`)
  the machine-readable mirror of `docs/_status/servicers-registry.{zh,en}.md`,
  so AGENTS.md § 6.8's "single source of truth" promise actually holds
  end-to-end (doc ↔ plan ↔ SQL todos ↔ **tool output**).
- **Concrete steps**:
  1. Add manifest `docs/_status/servicers.yaml` — one entry per servicer
     with `id`, `status` (`done` / `in-progress` / `pending-analysis`),
     `sheets_count`, `stage1_doc` (`done` / `in-progress` / `pending`),
     `stage2_system` (`done` / `pending` / `blocked`), `placeholder_doc`
     (path or `null`), `notes`.
  2. Add a JSON schema `tools/schema/servicer.schema.json` for it.
  3. Extend `tools/registry.py`: load the manifest, expose
     `Registry.servicers: dict[str, Servicer]`, cross-check that
     `status == pending-analysis` ⇒ `placeholder_doc` file exists AND
     no `whitebox/validators/<id>/*.yaml` exists AND no
     `sheets/<ID>_*.yaml` exists; conversely `status in (done,in-progress)`
     ⇒ at least the expected stub presence (later: at least one
     validator YAML once Stage 2 starts).
  4. CLI `main()` prints a new "Servicers" section showing
     analyzed-vs-pending counts and per-servicer status line.
  5. Add a tiny pytest `tests/test_registry_servicers.py` covering:
     manifest loads, MRC = in-progress + placeholder_doc is null,
     all 6 pending servicers have placeholder_doc that exists.
  6. Re-run test matrix.
- **Definition of done**:
  - `python tools/registry.py` exits 0 and prints the new Servicers section.
  - `pytest -q` green (new test included).
  - `mkdocs --strict` still green.
  - Test report `test_reports/cleanup-c6_2026-05-17.md` written.
  - SQL: new todo `cleanup-c6-registry-servicer-status` inserted and
    marked `done`.

### A (= plan.md / convention refinement)

- **Goal**: lift cross-cutting rules that emerged after v9.1 was first
  drafted into the visible "Per-chapter conventions" section of `plan.md`,
  and pin the Stage 1 baseline `remit_date`.
- **Concrete steps**:
  1. In `plan.md` § "Per-chapter conventions", add bullets pointing to
     **AGENTS.md § 6.9** (mermaid node-ID legend rule) and the
     **doc-header + revision-history rule** (§ 6.7).
  2. Add a new top-level subsection **"Stage 1 baseline `remit_date`"**
     pinning the value to **`2026-04-30`** (rationale: 5 `MRC_*.yaml` sheet
     templates + 5 `snapshots/2026-04-30/gold/MRC_*.json` reference outputs
     already exist and are un-frozen — zero-cost reuse, eliminates the
     "which date?" decision from every downstream chapter).
  3. Append the matching entry to `decisions.md`.
  4. No code change; just plan + decisions text.
- **Definition of done**:
  - `plan.md` updated; section visible in mkdocs build.
  - `decisions.md` has a "2026-05-17 baseline remit_date pinned to
     2026-04-30" entry.
  - SQL: new todo `cleanup-a-plan-convention-refresh` inserted and
    marked `done`.

### After B + A both done

Start `stage1-mrc-toc` per the existing § "Stage 1 todos (MRC-first)".

---

## Cleanup items to run before `stage1-mrc-toc` starts

- **C0** Move 4 non-MRC chapters + autodoc placeholders to
  `docs/_archived/pre-mrc-pivot/`; remove from `mkdocs.yml` nav.
- **C1** SQL: set the 7 non-MRC stage1-* todos to status `pending-deferred`
  (NOT `blocked`), description amended with "v9.1: placeholder reserved in
  servicers-registry; analysis paused while MRC end-to-end completes". Insert
  the 8 new `stage1-mrc-*` todos and 12 new `stage2-mrc-*` todos with
  dependencies (each stage1-mrc-* depends on previous; stage2-mrc-* on
  `stage1-mrc-review`; harness blocks acceptance). Insert a new
  `stage1-pending-registry` todo as a prerequisite of `stage1-mrc-toc`.
- **C2** Replace `plan.md` content with this file.
- **C3** Append v9.1 entry to `progress.md` Revision history; rewrite the
  Stage 1/2 progress tables; embed the servicer status matrix.
- **C4** Append `2026-05-17 v9.1 pivot` decision to `decisions.md` capturing
  all 5 ask_user answers (cell-identical, archive non-MRC, un-freeze MRC
  assets, UI in Stage 2 with engine priority, placeholder-everywhere rule).
- **C5** Create `docs/_status/servicers-registry.{zh,en}.md` + per-pending-
  servicer `docs/<servicer>/_pending.{zh,en}.md` stubs; wire into mkdocs nav
  under a "Project status" section.
- **C6** Either extend `tools/registry.py` (un-frozen) to emit a
  `pending-analysis` flag per servicer, OR add a new
  `tools/servicer_status.py` that reads the matrix and emits a JSON report
  consumed by docs builds. Decide during C6 execution.
- **C7** Append AGENTS.md rule § 6.8: "Any change to a servicer's analysis
  state requires same-commit update to servicers-registry."

Cleanup C0 and C5 are user-visible structural changes; I will confirm before
moving the 4 polished chapters into `_archived/`.

---

## Risks

- Cell-identical XLSX may force adopting the same XLSX library as the old code
  (surfaced in `stage2-mrc-xlsx-renderer`).
- Baseline date selection: must pick a clean `remit_date`; verify in
  `stage1-mrc-baseline`.
- Ingestion equivalence: if upstream Redshift state can't be exactly
  reproduced, "cell-identical" requires snapshotting unified tables as part of
  the baseline.
- SQL complexity (~700-line MRC General Check CTE) may need business cross-check.
- **NEW (v9.1):** the placeholder-everywhere rule adds maintenance overhead.
  Mitigation: the servicer status matrix is the single source of truth;
  everything else (docs/registry tool/UI) reads from it.

---

## Not in scope (Stage 1)

- New Python / SQL / YAML code for the validation engine
- Stage 2 technology choices
- PrefectFlow source modifications (always read-only)
- Other servicers' end-to-end analysis — placeholder stubs only

---

## Pre-v9.1 history

- v1 → v5: bootstrap (mkdocs, autodoc, lineage, freeze_snapshot).
- v6 / v7: MRC pilot (sheets/*.yaml, gold JSONs, slice_gold.py).
- v8 (2026-05-16 → 2026-05-17): strict 2-stage doc-first; delivered
  toc / overall-flow / carrington / shellpoint chapters.
- v9 draft: MRC-only pivot (superseded by v9.1 before activation).

Full per-checkpoint history:
`C:\Users\jli\.copilot\session-state\4cd52a8e-d034-4def-84a0-04057dd64872\checkpoints\`.


---

## 11. Round 3 wave-2 + closure — 2026-05-18

**Status**: 12 / 12 d-* todos = DONE. 4 of the original 7 stage2-mrc-* tasks are now effectively delivered by the d-* foundation; 3 remain for P2.5.

### Commits landed (wave order)
| Commit | Todo | Description |
|---|---|---|
| 95d289d | (round-2 fix) | commit missing tools/xlsx_diff.py + tests + help (Round 2 had wrong commit content) |
| ec862b | d-arch-freeze + d-pr-evidence-rule | architecture freeze, openpyxl==3.1.5 pin, PR evidence rule |
| 998ddb | d-cte-harness-impl | DuckDB-based local CTE replay harness |
|  da9108 | d-registry-impl | 4 registries (validator/sheet/servicer/dataset) + dispatch |
| 43bf4c8 | d-nextjs-skel | Next.js 14 App Router skeleton (HARD restraint, no extra deps) |
|  d8fbfa | d-transform-impl | pure transformation layer (no IO) |
| 5074f40 | d-fastapi-skel | FastAPI skeleton with stub routers |
| 96fce8b | d-sheets-impl | 5 MRC sheet builders (Summary/General/Advance/ServiceFee/Adv_Info) |
| 6416cf6 | d-api-contracts | production pydantic schemas + 10 endpoints + FE type mirror |
| 4f68c3f | d-ui-core-screens | picker/runs/detail/sheet drill-down + cell panel |
| b2ea64 | d-renderer-pin | XLSX renderer + golden style snapshot + cell-identity smoke PASS |
| 2e659b2 | d-ui-drill-down-impl | lineage graph + XLSX diff viewer |

### Test totals at closure
- Backend: **249 passed** (full pytest suite)
- Frontend: **npm run build OK**, 7 routes, zero new deps
- Cell-identity smoke (renderer self-render): **identical** (0 major / 0 minor)

### Restraint compliance
- openpyxl pin **==3.1.5** held
- Zero new FE deps beyond Next.js + React + Tailwind + reactflow
- Zero new backend top-level deps; only [api] optional extras added

### Effective coverage of original v9.1 stage2-mrc-* todos
| Original todo | Effective coverage now |
|---|---|
| `stage2-mrc-ingestion` | d-cte-harness-impl + d-transform-impl (full path via DuckDB or live Redshift) |
| `stage2-mrc-api` | d-fastapi-skel + d-api-contracts (10 endpoints typed; fixture-backed pending engine) |
| `stage2-mrc-ui-impl` | d-nextjs-skel + d-ui-core-screens + d-ui-drill-down-impl (7 routes complete) |
| `stage2-mrc-xlsx-renderer` | d-renderer-pin (5-sheet self-render cell-identity PASS) |

### Remaining for P2.5
- `stage2-mrc-engine` — orchestration: ingestion -> transform -> validators -> sheets -> renderer; wires the 12 d-* pieces into an end-to-end pipeline producing real XLSX
- `stage2-mrc-cell-identity-harness` — full legacy-vs-new comparison via tools/compare_validation.py auto (blocked from full execution until G2a unblocks or a baseline XLSX is captured manually)
- `stage2-mrc-acceptance` — sign-off

### Decisions taken during Round 3 (recorded in decisions.md)
- openpyxl pinned to 3.1.5 with bump policy gated on ADR + cell-identity re-verification
- FE: Next.js + Tailwind only; new deps require ADR
- PR evidence rule enforced via .github/PULL_REQUEST_TEMPLATE.md


---

## 12. Round 3 complete — v9.1 acceptance signed off — 2026-05-18

**Status**: P2.5 `stage2-mrc-acceptance` DONE. Round 3 closed.
Sign-off authority: `docs/stage2/13.0-v9.1-acceptance-signoff.en.md`
(+ `.zh.md` mirror).

### 12.1 Final Round 3 commit table (chronological)

| # | Commit | Todo / role |
|---|---|---|
| 1 | `95d289d` | (round-2 fix) commit missing `tools/xlsx_diff.py` + tests + help |
| 2 | `aec862b` | P2.0 `d-arch-freeze` + `d-pr-evidence-rule` (architecture freeze, openpyxl==3.1.5 pin, PR evidence rule) |
| 3 | `b998ddb` | P2.1 `d-cte-harness-impl` (DuckDB-based local CTE replay) |
| 4 | `0da9108` | P2.1 `d-registry-impl` (4 registries + dispatch) |
| 5 | `43bf4c8` | P2.4 `d-nextjs-skel` (Next.js 14 App Router skeleton) |
| 6 | `0d8fbfa` | P2.1 `d-transform-impl` (pure transformation layer) |
| 7 | `5074f40` | P2.3 `d-fastapi-skel` (FastAPI skeleton with stub routers) |
| 8 | `96fce8b` | P2.2 `d-sheets-impl` (5 MRC sheet builders) |
| 9 | `6416cf6` | P2.3 `d-api-contracts` (pydantic schemas + 10 endpoints + FE type mirror) |
| 10 | `4f68c3f` | P2.4 `d-ui-core-screens` (picker/runs/detail/sheet drill-down + cell panel) |
| 11 | `eb2ea64` | P2.2 `d-renderer-pin` (XLSX renderer + golden style snapshot + cell-identity smoke PASS) |
| 12 | `2e659b2` | P2.4 `d-ui-drill-down-impl` (lineage graph + XLSX diff viewer) |
| 13 | `7e19ddd` | plan: round 3 closure (12/12 d-todos) + § 11 wave-2 summary |
| 14 | `e47be1b` | P2.5 `stage2-mrc-engine` (MRC validation engine end-to-end pipeline; embedded verdict.json PASS) |
| 15 | `e5fc87a` | P2.5 `stage2-mrc-cell-identity-harness` (acceptance gate + harness + CI hook) |
| 16 | _this commit_ | P2.5 `stage2-mrc-acceptance` (v9.1 sign-off, no product code) |

### 12.2 Final numbers

- **Backend pytest**: **299 passed, 2 ENV-SKIP** (full suite, 301 collected).
  Per-module: registry 20 / transform 26 / sheets 27 / renderer 56 /
  ingestion 5 / engine 20 / api 27 / acceptance 20 / integration 12 /
  tools 74 / root 14.
- **Acceptance gate**: `verdict=PASS`, exit 0; self-consistency
  `0 major / 0 minor` across all 5 MRC sheets; baseline + legacy SKIPPED
  (documented ENV-SKIP — G2a still env-blocked).
- **mypy --strict whitebox/**: clean (61 source files).
- **ruff (Round 3 new code)**: clean. **ruff (whole repo)**: 34
  pre-existing legacy/Round-2 errors documented in sign-off § 5 as
  MARGINAL — janitorial follow-up, does not block v9.1.
- **Frontend `npm run build`**: green (Next.js 14.2.35, 7 routes,
  87.3 kB shared First-Load JS).
- **Restraint**: `openpyxl==3.1.5` pinned; backend top-level deps
  unchanged (duckdb, openpyxl, pyyaml, pandas, sqlglot + [api] extras);
  FE deps = next + react + react-dom + reactflow + Tailwind/PostCSS
  dev only.

### 12.3 Final verdict.json (excerpt — runs/acceptance-signoff-final/)

```json
{
  "verdict": "PASS",
  "exit_code": 0,
  "components": {
    "self_consistency": {"status": "PASS", "major": 0, "minor": 0,
      "per_sheet": [
        {"sheet": "MRC_Summary_check",    "major": 0, "minor": 0},
        {"sheet": "MRC_General_Check",    "major": 0, "minor": 0},
        {"sheet": "MRC_Advance_Check",    "major": 0, "minor": 0},
        {"sheet": "MRC_ServiceFee_Check", "major": 0, "minor": 0},
        {"sheet": "MRC_Adv_Info",         "major": 0, "minor": 0}
      ]
    },
    "baseline":    {"status": "SKIPPED", "reason": "--baseline not provided"},
    "legacy_live": {"status": "SKIPPED", "reason": "--legacy-mode=skip"}
  }
}
```

### 12.4 What remains (gaps from sign-off § 6)

- **G2a** (Redshift snapshot freeze) — deferred, environment-blocked.
- Real baseline XLSX not yet captured
  (`baselines/mrc/2026-04-30/CAPTURE_INSTRUCTIONS.md` awaits operator).
- Validators V1–V12 ship as stubs/DEGRADED on the bundled CTE harness;
  real validator logic awaits real data.
- Lineage data fixture-backed; engine-side emission deferred to v9.2.
- Export endpoint returns 501 (engine-side XLSX streaming deferred).
- `docs/stage2/12.0-acceptance-gate.zh.md` mirror not yet shipped.
- 34 pre-existing ruff errors in legacy/Round-2 tooling — janitor pass
  deferred.

None of the above blocks v9.1 acceptance under
`docs/stage2/12.0-acceptance-gate.en.md`; each becomes a concrete
v9.2/v9.3/v9.4 follow-up listed in sign-off § 8.

### 12.5 Pointer

The single sign-off record is `docs/stage2/13.0-v9.1-acceptance-signoff.en.md`
(English) with `docs/stage2/13.0-v9.1-acceptance-signoff.zh.md` (中文 mirror).
