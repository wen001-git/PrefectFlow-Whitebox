# 1.0 TOC & Scope / 章节地图与范围

> **文档用途 (Purpose)**：作为整本 MRC 章节的入口文档，明确 Stage 1 MRC 反向工程的范围、产物、源代码坐标，并把后续 7 章（1.1–1.7）的章节地图与依赖关系固定下来。
>
> **目标读者 (Audience)**：当前会话与后续会话的 Copilot CLI agent；项目维护者；任何想快速了解「MRC validation report 当前被分析到什么程度、下一步看哪个文档」的人。
>
> **修订历史 (Revision history)**
>
> | 日期 | 作者 | 变更 |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — 首版。v9.1 MRC-only 聚焦下的第一份正式章节。包含一处**对早期假设的更正**：MRC 实际上有 5 个 validator（含 `mrc_other_check`），而非早期 plan v9.1 草稿里写的 "4 个，缺 mrc_other_check"。详见 § 5 与 § 10。 |

# 1. MRC 章节：TOC 与范围冻结

## 1. 文档定位

本文档是 MRC 章节（`docs/mrc/`）的目录与「契约页」。它**不**含具体数据流分析、字段血缘或验证规则细节 —— 那些放在 1.1–1.6 各自的子章节里。本文档只回答四个问题：

1. **范围**：Stage 1 MRC 分析包含什么，不包含什么？
2. **坐标**：要分析的真实代码、SQL、配置、gold 文件分别在哪里？
3. **基线**：所有例子和 baseline XLSX 用哪一个 `remit_date`？
4. **地图**：1.1–1.7 七个子章节各产出什么、互相依赖什么？

## 2. 范围 (Scope)

### 2.1 在范围内 (In scope)

- 描述 MRC 这一个 servicer 的 **5 个 Prefect validator** 各自的输入、SQL/Python 逻辑、输出 DataFrame 的列。
- 描述这 5 个 DataFrame 如何被 `gen_remit_validation_report.py` 渲染为 **5 张 XLSX sheet**。
- 描述每个输出列的**计算血缘**（追到上游字段 / SQL 表达式 / 常量）。
- 描述每张 sheet 的**通过 / 失败 / 异常判定规则**（高亮列、阈值、双分支等）。
- 用 `2026-04-30` 这一个真实 `remit_date` 截取并冻结一份 **baseline XLSX**，作为 Stage 2 cell-identical 验收的真值。

### 2.2 不在范围内 (Out of scope)

- 任何 Stage 2 重建工作（新数据模型、新引擎、UI 等）—— 由 `stage2-mrc-*` todos 承担，且必须在 `stage1-mrc-review` 用户验收通过之后才能动。
- 其他 servicer（Carrington / Shellpoint / Arvest / CC5 / Selene / SLS / Scattered / 跨 servicer dataflow）的端到端分析 —— 这些目前处于 `pending-deferred`（见 [`docs/_status/servicers-registry.zh.md`](../_status/servicers-registry.zh.md)）。
- MRC 的 ingestion（vendor 文件如何变成 `mrc.portmrcremit*` 表）—— 仅在 1.1 raw data 章里**列出表名 + 简述来源**，不深挖 ingestion job。

## 3. Stage 1 baseline `remit_date`

> **Baseline `remit_date` = `2026-04-30`** （由 plan v9.1 § "Stage 1 baseline remit_date" 钉死）

所有后续章节（1.1–1.6）凡是给例子行、期望行数、gold 输出、baseline XLSX 截图时，都**默认**使用这个日期。

派生时间锚：

| 锚 | 推导方式 | 2026-04-30 时的值 |
|---|---|---|
| `remit_date` | 输入参数 | `2026-04-30` |
| `pre_date` | `remit_date - MonthEnd(1)` | `2026-03-31` |
| `fctrdt` | `get_fctrdt(remit_date)` | 由 `flow/remit_validation/utils.py` 决定（在 1.1 中确认） |
| `fctrdt_1m` | `get_fctrdt(pre_date)` | 同上 |
| `curr_month_end` | `remit_date` 本身 | `2026-04-30` |
| `pre_month_end` | `pre_date` | `2026-03-31` |

源码定位：`mrc_db.py:1-14`。

## 4. MRC 的 5 张 sheet

按 Validation Report XLSX 中的 sheet 出现顺序：

| # | Sheet 名 | 一句话定位 | 产出它的 validator | 高亮 (P0) 列 |
|---|---|---|---|---|
| 1 | `MRC_Summary_check` | 当期所有 MRC loan 的 remit 金额单行汇总 | `mrc_summary_check` | （无显式高亮） |
| 2 | `MRC_General_Check` | 每个 loan 的 remit vs daily「通用信息」对比（利率、下次到期、本金余额等） | `mrc_check_general_info` | 7 列：`intrate_diff_remitvsdaily` / `nextduedate_diff_remitvsdaily` / `begbal_diff_remitvsdaily` / `endbal_diff_remitvsdaily` / `deferredprincipal_diff_remitvsdaily` / `deferredint_diff_remitvsdaily` / `pandi_schedule_diff_remitvsdaily` |
| 3 | `MRC_Advance_Check` | 每个 loan 的 advance / recovery / escrow 余额变动 remit vs daily | `mrc_check_adv_balance` | 4 列：`escadv_diff_remitvsdaily` / `recovcorpadv_diff_remitvsdaily` / `nonrecovcorpadv_diff_remitvsdaily` / `totalcorpadv_diff_remitvsdaily` |
| 4 | `MRC_ServiceFee_Check` | 每个 loan 的 service fee：`portmrcremitloanlevelrecap` vs `portmonth` 差值 | `mrc_service_fee_check` | 1 列：`servicefee_diff` |
| 5 | `MRC_Adv_Info` | 当期 + 上期 advance 明细聚合（bucket × description × tran_code），含 MoM 比例 | `mrc_other_check` | （无显式高亮） |

XLSX 渲染源：`util/gen_remit_validation_report.py:1327-1356`。

## 5. MRC 的 5 个 validator（更正：是 5 个，不是 4 个）

> **更正说明**：plan v9.1 草稿与 2026-05-17 早些时候的 checkpoint 曾两次写到「MRC 只有 4 个 validator，缺 `mrc_other_check`」。**这是错的**。读源码 `mrc_validation.py` 可以看到第 136–158 行有完整的 `@task(name='mrc_other_check')`，且 `remit_validation.py:143` 把它的输出装入 `VALIDATION_TABLE_MAP['mrc_adv_info']`，最终生成 `MRC_Adv_Info` sheet。本章节、plan v9.1 servicer 状态表、decisions.md 都将以此为准。

| # | Validator 函数 | 源码 | 关键技术 | 输出 → sheet |
|---|---|---|---|---|
| 1 | `mrc_summary_check` | `mrc_validation.py:8-36` | 内联 SQL；对 `port.portmonth` 做 13 列 `sum()` 聚合 | `MRC_Summary_check` |
| 2 | `mrc_check_general_info` | `mrc_validation.py:57-72` | SQL 模板 `mrc_general_check`，替换 `input_fctrdt` / `input_curr_month_end` / `input_pre_month_end` | `MRC_General_Check` |
| 3 | `mrc_check_adv_balance` | `mrc_validation.py:39-54` | SQL 模板 `mrc_adv_validation`，同样三参数替换 | `MRC_Advance_Check` |
| 4 | `mrc_service_fee_check` | `mrc_validation.py:75-102` | 内联 SQL，3 表 join：`mrc.portmrcremitloanlevelrecap r` + `port.portmonth p` + `port.portfunding f` | `MRC_ServiceFee_Check` |
| 5 | `mrc_other_check` | `mrc_validation.py:105-158` | Python：两次跑 `_mrc_adv_info_sql`（curr fctrdt 与 fctrdt_1m），用 pandas merge 算 `amt_MoM = amt / amt_1m - 1` | `MRC_Adv_Info` |

所有 validator 都接受同一个 `MrcDB` 实例作为入参（`mrc_db.py:7-14`），并往返回的 DataFrame 上追加 `asofdate = remit_date` 列。

## 6. 2 个 SQL 模板

| 模板名 | 文件位置 | 被谁用 | 三参数 |
|---|---|---|---|
| `mrc_adv_validation` | `flow/remit_validation/servicer_validation_with_portdaily.py` | `mrc_check_adv_balance` | `input_fctrdt`, `input_pre_month_end`, `input_curr_month_end` |
| `mrc_general_check` | `flow/remit_validation/servicer_validation_with_portdaily.py` | `mrc_check_general_info` | `input_fctrdt`, `input_curr_month_end`, `input_pre_month_end` |

模板内具体 SQL（涉及的表、join、CTE、差值列定义）在 1.2 dataflow 与 1.3 sheets 中展开。

## 7. 编排入口 (Orchestration)

MRC 这一段在 `flow/remit_validation/remit_validation.py:134-144` 被串起来：

1. `mrc_db = MrcDB(remit_date, to_new_redshift, to_mysql)` —— 建立 DB 句柄。
2. `mrc_summary_df = mrc_summary_check(mrc_db)` → `VALIDATION_TABLE_MAP['mrc_summary_check']`
3. `mrc_general_df = mrc_check_general_info(mrc_db)` → `VALIDATION_TABLE_MAP['mrc_general_check']`
4. `mrc_adv_df = mrc_check_adv_balance(mrc_db)` → `VALIDATION_TABLE_MAP['mrc_adv_check']`
5. `mrc_service_fee_df = mrc_service_fee_check(mrc_db)` → `VALIDATION_TABLE_MAP['mrc_service_fee_check']`
6. `mrc_adv_info_df = mrc_other_check(mrc_db)` → `VALIDATION_TABLE_MAP['mrc_adv_info']`

`VALIDATION_TABLE_MAP` 的 5 个 MRC key 后续被 `gen_remit_validation_report.py` 消费成 5 张 sheet。`VALIDATION_TABLE_MAP` 中其他 servicer 的 key 与 MRC 无关，本章不涉及。

> 🔍 PENDING-ANALYSIS：上下游编排链（`compose_report_task` / `scattered_validation` / 邮件发送 / S3 写入）属于跨 servicer 范畴，由 [`docs/dataflow/_pending.zh.md`](../dataflow/_pending.zh.md) 跟踪，本章不展开。

## 8. 源代码引用索引

本章节后续 1.1–1.6 引用的源码都集中在以下文件，方便维护时一次性确认：

| 文件 | 行范围 | 说明 |
|---|---|---|
| `flow/remit_validation/mrc_db.py` | `mrc_db.py:1-14` | MRC DB 句柄；时间锚推导 |
| `flow/remit_validation/mrc_validation.py` | `mrc_validation.py:1-158` | 5 个 `@task` validator |
| `flow/remit_validation/servicer_validation_with_portdaily.py` | `mrc_adv_validation` + `mrc_general_check` 两段模板 | SQL 模板（具体行号在 1.2 中给出） |
| `flow/remit_validation/remit_validation.py` | `remit_validation.py:134-144` | MRC 编排段（5 个 validator 顺序调用） |
| `util/gen_remit_validation_report.py` | `gen_remit_validation_report.py:1327-1356` | 5 张 MRC sheet 的渲染契约（列定义 + 高亮列） |

## 9. 章节地图 (1.1 – 1.7)

后续章节按数据流方向组织。每一章交付 `docs/mrc/<name>.{zh,en}.md` 两份对齐双语，并在完成时新增一份 `test_reports/<todo-id>_YYYY-MM-DD.md`。

| 编号 | todo-id | 章节名 | 产出 | 状态 |
|---|---|---|---|---|
| 1.0 | `stage1-mrc-toc` | 本文档 | `docs/mrc/toc.{zh,en}.md` | 🚧 进行中 |
| 1.1 | `stage1-mrc-rawdata` | 原始数据与 unified 表 | `docs/mrc/rawdata.{zh,en}.md` | ⏳ 待开始 |
| 1.2 | `stage1-mrc-dataflow` | 端到端数据流（含 mermaid 图 + 图例） | `docs/mrc/dataflow.{zh,en}.md` | ⏳ 待开始 |
| 1.3 | `stage1-mrc-sheets` | 5 张 sheet 的逐 sheet 生成逻辑 | `docs/mrc/sheets.{zh,en}.md` | ⏳ 待开始 |
| 1.4 | `stage1-mrc-fields` | 每个输出列的字段级血缘 | `docs/mrc/fields.{zh,en}.md` | ⏳ 待开始 |
| 1.5 | `stage1-mrc-rules` | 验证规则目录（通过 / 失败 / 异常） | `docs/mrc/rules.{zh,en}.md` | ⏳ 待开始 |
| 1.6 | `stage1-mrc-baseline` | Baseline XLSX 截取与冻结 | `docs/mrc/baseline.{zh,en}.md` + `baselines/mrc/2026-04-30/validation_report.xlsx` | ⏳ 待开始 |
| 1.7 | `stage1-mrc-review` | 用户走读评审（Stage 2 开闸点） | （用户动作） | ⏳ 待开始 |

依赖：1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7。

## 10. 已知未知 / 暂定假设

- **关于 mrc_other_check 的更正**已在 § 5 写明。需要把这条更正同步回 `plan.md` Servicer status matrix（在 MRC 行的 notes 里去掉 "no mrc_other_check" 字样）和 `docs/_status/servicers-registry.{zh,en}.md` MRC 行 notes 字段。
- `get_fctrdt(remit_date)` 的具体逻辑（`flow/remit_validation/utils.py`）尚未细读 —— 1.1 raw data 章节将首次正式记录其推导规则与 2026-04-30 当天的具体值。
- 2 个 SQL 模板的完整源文本与 join 拓扑放在 1.2 dataflow 中展开，本章只给名字。
- Baseline 截取使用 `snapshots/2026-04-30/gold/MRC_*.json`（v8 冻结、v9.1 解冻）作为对比真值；如该 JSON 与重新跑出的 XLSX 在某些列上**不**完全对齐，1.6 baseline 章节将首先解释差异原因，再决定哪份作为 cell-identical 验收基准。

## 11. 跨 servicer 引用（占位说明）

凡是与其他 servicer 相关的概念（共享 SQL 模板、共享辅助表、跨 servicer 规则 `scattered_*` 等），本章遵循 plan v9.1 / AGENTS.md § 6.8 的占位规则：

- 出现处使用 `> 🔍 PENDING-ANALYSIS:` callout；
- 链接到 [`docs/_status/servicers-registry.zh.md`](../_status/servicers-registry.zh.md) 与对应 `docs/<servicer>/_pending.zh.md`；
- 不在本章假装已完成对那 servicer 的分析。
