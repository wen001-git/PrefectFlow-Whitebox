# PrefectFlow-Whitebox

> Bilingual / 双语 · **v9.1 ACCEPTED — Stage 2 development baseline (MRC)**

## Status (2026-05-18)

- ✅ **Stage 1 (MRC chapters 1.0–1.6)** — living docs, provisionally approved
- ✅ **Stage 2 v9.1 (MRC) — ACCEPTED as development baseline**
  - Sign-off: `docs/stage2/13.0-v9.1-acceptance-signoff.en.md` (+ `.zh.md`)
  - Acceptance gate `verdict=PASS` (self-consistency 0/0 across 5 MRC sheets)
  - 299 backend tests passing + 2 documented ENV-SKIP; `npm run build` green
  - Conditions for production cutover and known gaps: see sign-off § 7 / § 9
- ⏳ **v9.2+** — real validator logic, lineage emission, XLSX export streaming,
  Carrington / Arvest / CC5 / Selene / SLS / Shellpoint onboarding (incremental
  via the servicer registry)

## EN

**Purpose.** Reverse-engineer the existing **Validation Report** pipeline in
`C:\Users\jli\MyData\Copilot\PrefectFlow` and ship a complete, source-cited
whitebox documentation of how every Excel sheet, every field, and every
validation rule is produced, then deliver an MRC validation system that is
cell-identical to the legacy XLSX with an interactive UI.

**Status.** Stage 1 MRC chapters live; Stage 2 v9.1 ACCEPTED as MRC
development baseline (see Status above).

- ✅ `stage1-toc` — Table of contents (zh + en)
- ✅ `stage1-overall-flow` — Chapter 1.1, end-to-end flow with 6 inline workflow/dataflow diagrams
- ⏳ `stage1-carrington` → `stage1-shellpoint` → `stage1-arvest` → `stage1-cc5` → `stage1-selene` → `stage1-mrc` → `stage1-sls` → `stage1-scattered`
- ⏳ `stage1-dataflow` (cross-servicer lineage)
- ⏳ `stage1-review` (user walk-through, gates Stage 2)

See `plan.md` for the full v8 plan and `progress.md` for live status.

**Where to start (in order):**

1. `AGENTS.md` — onboarding rules; read first if you are an AI agent or new contributor.
2. `progress.md` — current state, last session, next concrete action.
3. `plan.md` — full v8 two-stage plan with frozen-asset table.
4. `docs/validation-report-logic/toc.en.md` — Stage 1 chapter map.
5. `docs/validation-report-logic/overall-flow.en.md` — Stage 1 chapter 1.1.
6. `decisions.md` — historical decisions with rationale (chronological).
7. `prompts.md` — verbatim user-prompt log.

**Scope.** Narrow ETL — Redshift / MySQL → validators → 40-slot XLSX.
Upstream vendor → raw schema → unified schema ingestion is **out of
scope** (referenced as a black-box layer in the lineage diagrams).

**Source repo is READ-ONLY.** Never edit
`C:\Users\jli\MyData\Copilot\PrefectFlow` from this repo.
`C:\Users\jli\MyData\Copilot\PrefectFlow-LearningLog` is also read-only.

**Frozen assets.** The bootstrap-era mkdocs site shell, the
`whitebox/validators/`, `sheets/*.yaml`, `snapshots/2026-04-30/gold/*`,
and all `tools/*.py` *except* `tools/stage_doc_checks.py` are **frozen**
during Stage 1 — they remain in the repo but are not extended or relied
upon. Stage 2 will decide whether to reuse them.

**End-of-stage rule.** Per `AGENTS.md` § 6.5, every Stage 1 chapter
must pass the test matrix (pytest + zh/en heading alignment +
source-citation existence + `mkdocs build --strict`) and have a report
under `test_reports/<todo-id>_YYYY-MM-DD.md` before being marked
`done`.

---

## 中文

**目的。** 反推 `C:\Users\jli\MyData\Copilot\PrefectFlow` 中现有
**Validation Report** 生成流程，输出一份带源码定位的完整白盒化文档：
讲清楚每个 Excel sheet、每个字段、每条校验规则是怎么算出来的。
**阶段 1 只写文字文档**（不写新代码、不做技术选型）；阶段 2 才设计
新的交互式白盒系统，且必须等阶段 1 用户 approve 后才启动。

**当前状态。** 阶段 1 进行中。

- ✅ `stage1-toc` —— 目录（中英双份）
- ✅ `stage1-overall-flow` —— 章节 1.1 整体流程 + 6 张内联工作流 / 数据流图
- ⏳ `stage1-carrington` → `stage1-shellpoint` → `stage1-arvest` → `stage1-cc5` → `stage1-selene` → `stage1-mrc` → `stage1-sls` → `stage1-scattered`
- ⏳ `stage1-dataflow`（跨 servicer 数据血缘章节）
- ⏳ `stage1-review`（用户 walk-through，阶段 2 的 gate）

完整 v8 计划见 `plan.md`，实时进度见 `progress.md`。

**阅读顺序（重要）：**

1. `AGENTS.md` —— onboarding 规则；AI agent 或新协作者必读。
2. `progress.md` —— 当前状态 / 上次 session / 下一步具体动作。
3. `plan.md` —— v8 两阶段完整计划 + 冻结资产表。
4. `docs/validation-report-logic/toc.zh.md` —— 阶段 1 章节地图。
5. `docs/validation-report-logic/overall-flow.zh.md` —— 阶段 1 章节 1.1。
6. `decisions.md` —— 历史决策 + 理由（按时间）。
7. `prompts.md` —— 用户 prompt 逐字日志。

**范围。** 窄 ETL —— Redshift / MySQL → validators → 40-slot XLSX。
上游 vendor → raw schema → unified schema 的入仓**不在本项目范围**
（数据流图中以黑盒层引用）。

**原仓库只读。** 本仓库内绝不修改
`C:\Users\jli\MyData\Copilot\PrefectFlow`；
`C:\Users\jli\MyData\Copilot\PrefectFlow-LearningLog` 同样只读。

**冻结资产。** bootstrap 阶段建好的 mkdocs 站壳、
`whitebox/validators/`、`sheets/*.yaml`、
`snapshots/2026-04-30/gold/*` 以及 `tools/*.py`（**除**
`tools/stage_doc_checks.py`）在阶段 1 全部**冻结** —— 文件留在 repo
不删、也不扩展、不依赖。阶段 2 再决定是否复用。

**End-of-stage 规则。** 详见 `AGENTS.md` § 6.5：每个 Stage 1 章节必须
通过测试矩阵（pytest + 中英 heading 对齐 + 源码引用存在性 +
`mkdocs build --strict`）且在 `test_reports/<todo-id>_YYYY-MM-DD.md`
留下报告，才能在 SQL 中标记 `done`。
