# Decisions log

> Append-only. One bullet per meaningful decision.
> Format: `YYYY-MM-DD — <decision> — <one-line rationale>`.
> Newest at the bottom.

---

## 2026-05-16 — Initial bootstrap decisions (from plan v6 discussion)

- **2026-05-16 — Drop Dagster; use plain Python + YAML + MkDocs + DuckDB + sqlglot stack** — PrefectFlow validators are Python wrappers around Redshift SQL, not pure SQL; DBT would force Python→SQL rewrite (bigger lift); Dagster's main value is orchestration which Prefect already provides upstream.
- **2026-05-16 — Doc-first applied per validator, not per project** — Avoids front-loading 47 validator docs before the doc infrastructure is empirically validated (would cause schema-rework cascade).
- **2026-05-16 — Pilot servicer = MRC (5 validators)** — Enough validators to stress-test multi-validator + multi-sheet lineage; CC5 (2 validators) is too small and would give false confidence.
- **2026-05-16 — Equivalence target = data-equivalent, not bit-equivalent** — Per-sheet `(sorted_row, column, value)` tuple equality after type normalization + 1e-6 float tolerance; cell format/sheet order/column widths may differ; original bugs go to `docs/known-deltas.md` rather than being reproduced (stronger audit evidence).
- **2026-05-16 — YAML schema is two-layer: validators + sheets/columns** — A separate `sheets/<sheet>.yaml` with per-column metadata is required for per-field whitebox display (validator-only schema cannot answer "what's the logic for this column?").
- **2026-05-16 — Use `sqlglot` for column-level lineage auto-extraction** — Manual lineage maintenance is unsustainable; sqlglot parses validator SQL and derives `output_col ← f(input_table.col, …)` automatically, back-filled into sheet YAMLs.
- **2026-05-16 — ETL scope = narrow (Redshift → validators → report)** — Build for the environment that already works (Vault token + Redshift VPN + `run_remit_validation.py` wrapper, verified in LearningLog session 04). Upstream vendor-file ingestion is out of scope; black-boxed in the doc site. Reason for narrowing from v5: avoid introducing unverified prerequisites (vendor file accessibility, ingestion ETL complexity).
- **2026-05-16 — Pilot reference date = 2026-04-30** — Gold XLSX already exists at `PrefectFlow-LearningLog/docs/remit-validation-report/20260430/`.
- **2026-05-16 — Repo location = sibling at `C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox\`** — Keeps source repo read-only; mirrors the LearningLog pattern.
- **2026-05-16 — Doc conventions = README + AGENTS.md + plan.md + progress.md (merged progress+handoff) + decisions.md + prompts.md** — Same pattern proven in PrefectFlow-LearningLog; explicitly merge progress + handoff because they answer the same question at different timescales.
- **2026-05-16 — Spike gate after MRC pilot, 3-way decision** — Continue rolling / Refactor infra first / Scope cut. Prevents over-commitment before the doc infra is validated end-to-end on a real servicer.

## 2026-05-16 — MRC validator 实施顺序：v1 → v4 → v5 → v2 → v3
理由：先做 v1（单行聚合，最简）建立 YAML+harness 闭环信心；v4 次小且 SQL 自包含；v5 提早隔离 Python merge 这个不同质点；v2/v3 SQL 最大（~30 列），放最后让 sqlglot 在小 case 验证过后再压力测试，且 v2/v3 结构相近可复用。来源：docs/servicers/mrc/scope.{en,zh}.md。

## 2026-05-16 — Process rule: never self-mark human-review steps as done

**Triggered by**: 把 Phase 1.5 自动化测试通过当成整个 Phase 1.5 done，跳过了 plan
里明确写的"手工 review：站点上点开占位 sheet → 看到占位 column 的完整逻辑卡片"。
之后又顺势把 mrc-scope / mrc-sheets-yaml / mrc-gold 全标 done，但用户从未审阅过。

**Rule**:

1. 任何 plan / progress 中显式写了"手工 review"、"用户审阅"、"用户确认"、
   "business review" 等需要用户参与的步骤，**只有用户明确说"通过"才能标 done**。
   AI 不能自行勾掉，也不能默认"用户没说话就是 OK"。
2. 跳过 plan 里的步骤时必须**主动告诉用户**，并在 progress.md 里用 `[/]`
   或 `⏳` 标出"未完成"，绝不能用 `[x]`。
3. 当一个 phase 的 gate（如 Phase 1.5 → Phase 2 的"全过才能进 Phase 2"）
   未满足时，**所有依赖该 phase 的下游 todo 必须暂停**，不能因为"看上去可以做"
   就继续。
4. 每个 phase 结束时，列出本 phase plan 里的每一条要求，逐条说明：
   - 自动化部分完成情况
   - 需要用户参与的部分（review/approve）— 是否已请用户做、用户是否回复

## 2026-05-16 - 阶段 1 文档采用双语并行 / Stage 1 docs go bilingual paragraph-pair

中文先一段，紧跟英文一段，同一文件内交替。不再拆 .zh.md / .en.md 分文件。

Each Chinese paragraph is immediately followed by its English counterpart in the same file. Stop splitting into .zh.md / .en.md i18n variants for Stage 1 deliverables.


## 2026-05-16 (revised) - 阶段 1 文档恢复分文件双语 / Stage 1 docs revert to split-file bilingual

用户反馈：段对段交替阅读体验差。改回独立 .zh.md / .en.md 两个文件。

User feedback: paragraph-pair interleaving hurts readability. Reverting to separate .zh.md / .en.md files per chapter.


## 2026-05-16 - End-of-stage 自动测试 + 测试报告规则 / Mandatory end-of-stage tests + report

每个 stage todo（阶段 1 章节、阶段 2 交付物）完成时必须：跑测试矩阵 → 写 test_reports/<todo-id>_YYYY-MM-DD.md → 全 PASS 才能 done。规则细节见 AGENTS.md § 6.5 / 6.6。

Every stage todo (Stage 1 chapter or Stage 2 deliverable) must run the test matrix, produce a report under test_reports/<todo-id>_YYYY-MM-DD.md, and only then be marked done. Full rule in AGENTS.md sections 6.5 / 6.6.


## 2026-05-17 — v9.1 pivot to MRC-only with placeholder-everywhere rule

- **2026-05-17 — Scope narrowed to MRC servicer only** (user prompt 37) — analysis bandwidth focused on one servicer end-to-end (raw → unified → validators → 5 sheets → XLSX); other servicers retain placeholder stubs so they are not forgotten.
- **2026-05-17 — Stage 2 equivalence bar = cell-identical XLSX** (ask 1 → option A) — sheet names, sheet order, column order, headers, every cell value, and highlight colors must match byte-for-byte vs a frozen production baseline; supersedes the v6 `data-equivalent'' bar for MRC.
- **2026-05-17 — Non-MRC chapters archived, not deleted** (ask 2 → option A) — 	oc / overall-flow / carrington / shellpoint (zh+en) move to docs/_archived/pre-mrc-pivot/, removed from mkdocs nav, kept as cross-servicer pattern reference.
- **2026-05-17 — Frozen pre-v8 MRC pilot assets un-frozen as Stage 2 inputs** (ask 3 → option A) — sheets/MRC_*.yaml, gold JSONs, whitebox/validators/, related tools become live starting points; not bound by their old structure (rewrite freely).
- **2026-05-17 — Stage 2 includes interactive UI from prompt 19** (ask 4 → option 2) — 8 features (date/servicer picker, per-sheet logic viewer, lineage, pass/fail explanations, validator details, export, comparison) ship as part of Stage 2; engine and logic correctness take priority over UI polish; UI lightweight initially but must already expose validation transparency.
- **2026-05-17 — Placeholder-everywhere rule for pending servicers** (user prompt 38) — every plan/doc/registry/lineage/architecture artifact must reserve explicit placeholders for un-analyzed servicers (arvest/cc5/selene/sls/scattered/dataflow). Single source of truth = servicer status matrix in plan.md, mirrored into docs/_status/servicers-registry.{zh,en}.md and validator registry tool output. AGENTS.md gains § 6.8 enforcing same-commit registry updates.
- **2026-05-17 — SQL status for paused non-MRC todos = pending-deferred, not locked/rozen** — keeps them visible in active todo queries so they are not silently dropped; differentiates from truly cancelled work.
- **2026-05-17 — Mermaid node-ID legend rule (AGENTS.md § 6.9)** — any dataflow figure that uses short IDs (`T#` / `V#` / `SH#` / `R#` / …) must be followed immediately by a legend table mapping each ID to its real source/business name, plus the one-sentence reminder that IDs are display-only cross-references. Triggered by user prompt 39 (Shellpoint screenshot with unexplained `SH1` / `V2` in prose). Applied retroactively to the 4 archived chapters and promoted into plan.md `Per-chapter conventions`.
- **2026-05-17 — Stage 1 baseline `remit_date` pinned to 2026-04-30** — all Stage 1 MRC chapters cite this single date for example rows, expected counts, and baseline XLSX captures. Rationale: 5 `sheets/MRC_*.yaml` + 5 `snapshots/2026-04-30/gold/MRC_*.json` already exist for this date (un-frozen at v9.1), so reuse is zero-cost and removes the "which date?" decision from every chapter. Stage 2 cell-identity harness will parameterize over `(servicer, remit_date)` later; Stage 1 needs only one date.
- **2026-05-17 — Registry tool servicer-state awareness (cleanup C6 / B step)** — `docs/_status/servicers.yaml` is the machine-readable mirror of `docs/_status/servicers-registry.{zh,en}.md`; loaded + cross-checked by `tools/registry.py`. Pending-analysis servicers must have an existing `placeholder_doc` and no validator/sheet YAMLs; analyzed servicers must clear `placeholder_doc`. Covered by `tests/test_registry_servicers.py`.

- 2026-05-17 — MRC validator count corrected to 5 (incl. `mrc_other_check`) — earlier plan v9.1 drafts and 2 checkpoints stated "4 validators, no mrc_other_check"; source re-read of `mrc_validation.py:136-158` + `remit_validation.py:143` confirms `mrc_other_check` is a fully-defined `@task` whose output renders the `MRC_Adv_Info` sheet. Propagated to `docs/_status/servicers.yaml` (registry md was already correct) and recorded in `docs/mrc/toc.{zh,en}.md` § 5.
- 2026-05-17 — Project rule AGENTS.md § 6.10 / User rule § 7 added: diagram + text co-requirement — any workflow / dataflow / ETL / validation flow / system-interaction doc must include both a diagram and a 5-bullet textual explanation (business purpose, execution flow, input/output, key transformations, dependencies/assumptions); complex logic needs an overview + decomposed sub-process diagrams. Applied retroactively to `docs/mrc/dataflow.{zh,en}.md` (v2 refine): added 5 per-validator sub-diagrams (Figures 1.2.4 – 1.2.8) and 5-bullet blocks under every figure; renumbered sequence diagram 1.2.7 → 1.2.9. Tests: 14/14 PAIRS align, 510 citations PASS, pytest 14/14, mkdocs --strict ✅.

- **2026-05-17 — MRC 章节引用风格统一 (xref readability overhaul)** — 所有跨章节引用必须采用三元素形式 `<num> <Title> (<file>.md)`，例如 `1.4 字段定义 (1.4-fields.zh.md)` / `1.4 Field Definitions (1.4-fields.en.md)`。单一真相源 = `docs/mrc/_chapter-index.md`（任何章节名/文件名变更必须先在该文件落地，再传播到其它文档）。传播工具 = `tools/rewrite_xrefs.py` + `tools/cleanup_xrefs.py`（idempotent）。执行范围：`docs/mrc/*.md` × 12 + `progress.md` + `test_reports/stage1-mrc-*.md` × 8；自引用例外 = 同文件内 `§ 4.1` 无需带章节名；非 MRC 章节（`1.2.1` Carrington / `1.2.2` Shellpoint）保留原编号方案。变更记录 = `test_reports/stage1-mrc-xref-readability_2026-05-17.md`。验证：17/17 PAIRS + 698 citations PASS, pytest 14/14, mkdocs --strict ✅。理由：长 reverse-engineering session 中数字 ID 难记、对 AI context 不友好；三元素形式同时给人类和 AI 提供消歧。

- **2026-05-17 — MRC sheet 级 Business purpose / 业务用途 子章节强制** — 每张 MRC Validation Report sheet 在 docs/mrc/sheets.{zh,en}.md 与 docs/mrc/fields.{zh,en}.md 的对应章节都必须有 ### Business purpose / 业务用途 子章节，解释：业务用途、业务问题、数据口径、读者、设计意图 / 高亮理由、常见失败场景、风险 / 对账动机。采用**无编号**子章节以保留 X.1/X.2 既有编号；hidden 标记 <!-- BUSINESS-PURPOSE-V1 --> 保 idempotency。sheets.*.md 侧着重页面 / 渲染 / 读者，ields.*.md 侧着重列血缘 / 维护者，两侧用 Division with bullet 明确分工。工具：	ools/insert_business_purpose.py + 	ools/clean_business_purpose_label.py。验证：17/17 PAIRS + 698 citations PASS, pytest 14/14, mkdocs --strict ✅。变更记录 = 	est_reports/stage1-mrc-business-purpose_2026-05-17.md。理由：从代码逆向演进到业务 + 数据 + validation 语义——让 BA / ops / validators / 重写者读懂为什么有这一页，而不只是代码怎么写。

- **2026-05-17 — MRC 章节 1.6 Baseline XLSX Behavior 落地** — docs/mrc/baseline.{zh,en}.md 作为 (MRC, 2026-04-30) 实例的渲染契约，源自 gen_remit_validation_report.py:19-86, 1157-1798 与 5 个 column helper / 5 个 sheet 注册条目；每条契约带 [FROM-CODE] 或 [VERIFY] 标签，§ 9 列出 12 项必须实测的 [VERIFY]（V1-V12），全部升级到 [CONFIRMED] 才能开闸 Stage 2 acceptance。物理 XLSX 通过 	ools/freeze_baseline.py mrc 2026-04-30 产出（待实现，属 mrc-source-baseline todo）。新增 nav 条目 1.6 Baseline: mrc/1.6-baseline.md；aselines/ 目录骨架已建（含 README 与 .gitkeep）。验证：18/18 PAIRS + 734 citations PASS（+36），pytest 14/14，mkdocs --strict ✅。变更记录 = 	est_reports/stage1-mrc-baseline_2026-05-17.md。

- **2026-05-17 — MRC 章节文件名前缀化** — docs/mrc/{toc,rawdata,dataflow,sheets,fields,rules,baseline}.{zh,en}.md 全部重命名为 1.N-{base}.{lang}.md（与文档 H1 编号一致，与 1.x xref 约定对齐），文件浏览器侧栏可直接按序号排序；同步更新 mkdocs.yml nav、	ools/stage_doc_checks.py PAIRS、	ools/insert_business_purpose.py / clean_business_purpose_label.py 内的硬编码路径、docs/mrc/_chapter-index.md 基名列、_chapter-index-snippet.{zh,en}.md、所有 test_reports/*、progress.md、decisions.md 中的 xref。_archived/ 路径保留旧名（归档不动）。验证：18/18 PAIRS ALIGN OK、734 citations PASS、pytest 14/14、mkdocs --strict ✅。

- **2026-05-17 — G1 (stage1-mrc-review) closed: provisional sign-off with iterative refinement allowed** — 用户决定 MRC Stage 1 章节 1.0-1.6 当前覆盖度已可接受，剩余的 minor gaps（1.6 § 9 V1-V12 等 [VERIFY] 项、1.4 § 5/§ 6 几处 inferred 字段、1.3 几处 assumption 块）不阻塞 Stage 2 推进；后续以 incremental refinement 方式回写。规则化为 AGENTS.md § 6.11 (living docs + 3-tier marker [CONFIRMED] / [VERIFY] / [FOUND-DURING-STAGE2])。Stage 2 实现仍受 2 个 hard gate 约束：G2 (mrc-snapshot + mrc-source-baseline 产出 aselines/mrc/2026-04-30/validation_report.xlsx) + G3 (stage1-mrc-baseline-verify 把 V1-V12 升到 [CONFIRMED])。**Stage 2 设计层（feature-list / SRS / data-model / ui-design / dev-plan + 新增 extensibility-spec）即刻开闸**，可与 G2/G3 并行推进。SQL todo 状态：done +5 (G1 + 4 helper)、新增 2 个 (stage1-mrc-baseline-verify blocked, stage2-mrc-extensibility-spec pending)、design-tier 5 个由 blocked → pending；impl-tier 7 个继续 blocked 在 G2+G3+extensibility-spec 上。

- **2026-05-17 — G2 redefinition (`gate-G2`): from "freeze Redshift" → "freeze the input dataset"** — 用户决定公司 Redshift 数据库本身无法冻结；G2 改为冻结**产出 MRC `2026-04-30` validation report 所需的精确输入数据集**到本地。拆为两个子门：**G2a (`mrc-snapshot`)** = 把 5 个 MRC validator 实际读取的所有 Redshift 表 / SQL / 过滤后数据集导出到 `baselines/mrc/2026-04-30/input_snapshots/`（Parquet 优先，CSV 可选），每个数据集都有 `_manifest.json` 条目（含 `source` / `export_sql_path` / `filter` / `exported_at` / `exporter` / `format` / `path` / `row_count` / `column_count` / `columns[]` / `sha256_file` / `sha256_canonical_rows` / `redshift_session`）+ 逐字 SQL 存 `_export_queries/*.sql`；**G2b (`mrc-source-baseline` + `mrc-gold`)** = 用 Parquet-reading shim 替换 Redshift adapter，跑**原版** `flow/remit_validation` MRC 代码 → 产出 `validation_report.xlsx` + `manifest.json`，与 `PrefectFlow-LearningLog/docs/remit-validation-report/20260430/` 的 gold XLSX 对账。**G2a 必须由有 Redshift VPN+凭据的人执行**（用户或同事）；agent 负责写 `tools/freeze_snapshot.py` + `tools/legacy_adapter.py`，并在 snapshot 落地后完成 G2b 与 G3。**Stage 2 运行时不再依赖 live Redshift**——本地 frozen snapshot 是可复现性的唯一来源。存储默认走 Git LFS（`baselines/**/*.parquet` + `baselines/**/*.xlsx`），manifest + SQL 作为普通文件提交。详细 binding spec 在 session plan.md § 4.2。

## 2026-05-17 — G2a A1 — SQL coverage scan complete

- **2026-05-17 — G2a A1 deliverable shipped**: exhaustive MRC SQL coverage scan completed
  via enhanced `tools/freeze_snapshot.py plan` (v2.0). Scanner upgraded from naive 2-file
  AST scan (found 3 SQL strings) to a recursive import-walker that follows `flow/` import
  edges transitively and handles 8 SQL-detection patterns. Re-scan of MRC entry files
  (`mrc_validation.py`, `mrc_db.py`) + transitive imports (5 files total) found **21 SQL
  strings** (8 MRC-relevant), up from 3. The 2 chapter-1.2-listed templates previously
  missed (`mrc_adv_validation` ~50 lines and `mrc_general_check` ~71 lines, both in
  `servicer_validation_with_portdaily.py`) are now detected. All 5 chapter-1.2 catalog
  entries confirmed ✅. Coverage delta section in `_coverage.md` shows **no A2 targets**
  (zero templates still missing). Output: 21 `.sql` files under
  `baselines/mrc/2026-04-30/input_snapshots/_export_queries/template/`, updated
  `_plan_index.json`, and `_export_queries/_coverage.md`. Scanner gains `--min-expected`
  flag (default 5) for CI gate enforcement.

## 2026-05-17 — G2a A3: placeholder resolver landed

- **2026-05-17 — G2a A3 — placeholder resolver `--resolve` flag added to `freeze_snapshot.py`** — Operator review burden drops to "read resolved SQL, confirm, run"; resolver handles `{mrc_db.fctrdt}`, `{service}`, `{fctrdt}` f-string placeholders + `input_fctrdt`/`input_curr_month_end`/`input_pre_month_end` `.replace()`-style substitutions; `_mrc_adv_info_sql` fans out to 2 resolved variants (fctrdt=2026-05-01 + fctrdt=2026-04-01). `_bindings.json` at `baselines/mrc/2026-04-30/input_snapshots/` is externalisable via `--bindings`.

## 2026-05-17 — G2a A6 — Redshift dependency catalog

- **2026-05-17 — G2a A6: catalog all Redshift dependencies in one document; mask all sensitive values** — Rationale: G2a is operator-only because it requires VPN access + HashiCorp Vault token that the agent cannot possess; the catalog gives any operator a single prerequisite checklist without needing to spelunk `PrefectFlow/` source. Sensitive values (hostname, credentials, Vault token, IAM ARN) replaced with `<masked>` / `<replace-with-actual>` placeholders; hints provided (Vault path `prefect-secret/db/redshift`, env vars `BUILDENV` / `*_PREFECT_VAULT_TOKEN`). Schemas catalogued: `port` (4 tables), `mrc` (4 tables directly queried by validators); 13 `[VERIFY]` markers for unconfirmed row counts and latencies. Catalog: `docs/mrc/_g2a-redshift-dependencies.{zh,en}.md`. Cross-references added to `docs/mrc/1.1-rawdata.{zh,en}.md`. Driver: HashiCorp Vault via `hvac`; `redshift_connector` Python package; no AWS Secrets Manager or IAM federation found in code.

## 2026-05-17 — G2a A4 — manifest verifier landed

- **2026-05-17 — G2a A4: reeze_snapshot.py verify subcommand added (v2.2)** — Adds 8-check validator (C1 coverage parity, C2 schema completeness, C3 file+checksum, C4 SQL hash binding, C5 column schema sanity, C6 fan-out consistency, C7 bindings doc [strict], C8 storage policy [strict]). Exits 0/1/2 for pass/core-fail/strict-fail. --json writes _verify_report.json; --verbose prints per-entry detail. Pre-export smoke run fails gracefully with operator-readable list of what's missing. 16 tests under 	ests/tools/test_freeze_verify.py.


## 2026-05-17 — G2a A5 — operator runbook landed

- **2026-05-17 — G2a A5: bilingual operator runbook + .env.example shipped** — Rationale: all G2a Track A agent-doable tooling (A1–A4, A6) is complete; the only remaining work to close G2a is the operator export run. The runbook (	ools/docs/g2a-operator-runbook.{en,zh}.md) gives any operator a single document to execute the full freeze workflow end-to-end: pre-flight checklist (VPN, Vault, Python env), Step 1 plan --resolve, Step 2 SQL review, Step 3 export snippet (copy-pasteable Python, outside the repo), Step 4 _manifest.json schema + worked example, Step 5 erify with exit-code table, Step 6 commit + hand-off instructions, credentials do-not-commit checklist, and troubleshooting for all 5 known failure modes (C1/C2/C3/C6 verify failures + Vault expiry + unresolved placeholders). .env.example added to project root (.env already gitignored). G2a Track A is now tooling-complete; operator export is the sole remaining step.


## 2026-05-18 — Strategy pivot: live legacy-vs-new comparison

**Trigger**: G2a environment-blocked (no Redshift/VPN/Vault credentials available).
**Decision**: Pivot validation strategy temporarily.
- G2a (frozen snapshot) → deferred / environment-blocked enhancement
- G2b old (parquet-shim replay) → deferred
- G2b-LIVE (new hard gate) → live legacy-vs-new XLSX comparison harness validated end-to-end
- G3 → incremental V1-V12 confirmation via per-PR comparison evidence (no big-bang sweep)

**Rationale**: highest project risk is behavioral mismatch with legacy; need a trustworthy
validation mechanism before scaling implementation. Frozen-baseline ideal preserved as
long-term migration target.

**Scope of pivot**:
- Allowed: Stage 2 architecture / data model / validator framework / UI / lineage / renderer / MRC validator impl (after G2b-LIVE closes)
- Required: comparison-run evidence per impl PR
- Preserved: § 4.2 / § 4.4 (long-term ideal); A1-A6 tooling stays

**References**: plan.md § 9; docs/stage2/10.0-validation-strategy.{zh,en}.md

- 2026-05-18 — xlsx_diff uses two openpyxl loads per file (data_only=True for values, data_only=False for formulas+styles) — correctness requires separate reads since openpyxl cannot return both formula string and cached value in a single load.

## 2026-05-18 — Round 2 C4 — comparison orchestrator landed

- **2026-05-18 — compare_validation.py orchestrator shipped (C4)** — `tools/compare_validation.py` provides two subcommands: `compare` (Mode A: manual paths) and `auto` (Mode B: invokes C2+C3 then calls C1 as import). Produces `comparison_report.html` (enriched with run-context banner), `comparison_report.json` (C1 report + both metadata sidecars), `verdict.json` (top-level PASS/MINOR_DIFFS/MAJOR_DIFFS/ERROR with warnings + next-steps), and `comparison_report.log`. Exit codes mirror C1 (0/1/2/3). Auto dry-run prints orchestration plan without executing C2/C3. Calls C1 via module import (faster + better error propagation); C2/C3 via subprocess (isolation + creds). 12 tests under `tests/tools/test_compare_validation.py`. Operator doc: `tools/docs/compare_validation.md`. All 76 tests pass; `stage_doc_checks.py` 24/24 ALIGN OK + 798 citations PASS.

## 2026-05-18 — Round 2 C5 — comparison harness end-to-end validation passed; G2b-LIVE gate CLOSED

- **2026-05-18 — Round 2 C5 passed; G2b-LIVE gate closed** — 	ests/integration/comparison/test_harness_e2e.py delivers 12 integration tests (S1-S11 + fixture reproducibility). All 12 pass green in 18.9 s on first run. Exercises C1+C3+C4 in true subprocess end-to-end workflows covering all 8 required scenarios plus 3 optional. S7 asserts all 4 documented C3 perturbations (value_diff / font_diff / missing_row / extra_sheet) are detectable. No xfails; no follow-up todos created. Full suite (88 tests) passes; stage_doc_checks.py 798 citations clean. Gate status: G2b-LIVE closed. Stage 2 implementation tier (stage2-mrc-*-impl) unblocked pending user go-ahead.

## 2026-05-18 — Round 3 architecture freeze (P2.0)

- **Repo layout** — extend `whitebox/` with sub-packages (registry, ingestion, transform, engine, sheets, renderer, api); Next.js frontend lives at `apps/web/`. No moves of existing files.
- **openpyxl pinned to ==3.1.5** — cell-identity stability is contractual (Round 2 C5 verified). Any bump requires ADR + full cell-identity re-verification via `tools/xlsx_diff.py`.
- **Python 3.10.x kept** — Prefect ecosystem compatibility.
- **Backend = FastAPI >=0.115** — async-native, OpenAPI for FE codegen.
- **Frontend = Next.js ^14.2 + Tailwind only** at start — NO Redux/Zustand/tRPC etc. until justified by ADR (per plan.md § 10.2 restraint).
- **PR evidence rule** — any PR touching engine/sheets/renderer/validators/transform/ingestion/registry must attach `compare_validation.py auto` verdict.json. MAJOR_DIFFS = block merge. Enforced via `.github/PULL_REQUEST_TEMPLATE.md`.
- **Q1-Q4 user decisions** recorded in plan.md § 10.1: G2a deferred / Next.js+FastAPI / pin openpyxl / G1 archive as living docs.
- **Round 2 bug fix** — commit `95d289d` lands the actual `tools/xlsx_diff.py` + tests; original 7058ec8 had wrong message vs content. Discovered during P2.0 audit.

- **2026-05-18 — Engine `DEGRADED` covers DuckDB binder/catalog errors** — schema mismatches between fixture CSVs and the resolved SQL are treated identically to missing fixtures (degraded sheet, not ERROR), so a partial CTE harness can run end-to-end. `ERROR` is reserved for engine-internal bugs.
- **2026-05-18 — API engine backend opt-in via `ENGINE_BACKEND=live`** — default stays `fixtures` so the FE contract test pack is unaffected. Live mode currently swaps only the `/runs` and `/runs/{id}/sheets` endpoints; cell/diff/lineage/export still serve fixtures until their wiring lands.
- **2026-05-18 — Acceptance-gate policy (P2.5 `stage2-mrc-cell-identity-harness`)** — v9.1 cell-identity gate split across two equivalent surfaces: `tests/acceptance/mrc/` (pytest tier) and `tools/acceptance_gate.py` (CLI tier). Three modes: self-consistency (always on, FLOOR — any diff → MAJOR), baseline diff (when `baselines/mrc/<date>/validation_report.xlsx` present; ENV-SKIP otherwise), legacy live (when `ACCEPTANCE_LEGACY_LIVE=1` + Vault creds present; ENV-SKIP otherwise). MAJOR dimensions (`value` / `formula` / `merged_cells` / `structure`) are NEVER allowlistable; MINOR dimensions allowlistable only via JSON entry with `ADR_ref`. CI workflow `.github/workflows/acceptance-gate.yml` runs self-consistency on every PR and the full gate on `main` push / `workflow_dispatch`. ENV-SKIPs are not failures. See `docs/stage2/12.0-acceptance-gate.en.md`.
