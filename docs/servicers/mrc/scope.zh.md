# MRC servicer —— 范围（scope）

> 2026-05-16 从只读源仓库抽取。
> 来源：`flow/remit_validation/mrc_validation.py`、`flow/remit_validation/servicer_validation_with_portdaily.py`、`flow/remit_validation/remit_validation.py`、`util/gen_remit_validation_report.py`。

## Validators（5 个）

| # | Validator（task 名） | 产出 sheet | 源码位置 | 字段数 | 机制 |
|---|---|---|---|---|---|
| 1 | `mrc_summary_check` | **MRC_Summary_check** | `flow/remit_validation/mrc_validation.py:8-36` | 14 | 从 `port.portmonth` 取 `servicer='MRC'` 做聚合求和，单行结果。 |
| 2 | `mrc_check_general_info` | **MRC_General_Check** | `flow/remit_validation/mrc_validation.py:57-72` + SQL 位于 `servicer_validation_with_portdaily.py:635-701` | ~30 | 贷款级 join：`portmonth`（remit）vs `basic_data_daily_loan_common`（daily），diff 列高亮。 |
| 3 | `mrc_check_adv_balance` | **MRC_Advance_Check** | `flow/remit_validation/mrc_validation.py:39-54` + SQL 位于 `servicer_validation_with_portdaily.py:583-632` | ~25 | 贷款级 advance 余额对账：escrow / 可回收 corp adv / 不可回收 corp adv，remit vs daily。 |
| 4 | `mrc_service_fee_check` | **MRC_ServiceFee_Check** | `flow/remit_validation/mrc_validation.py:75-102` | 9 | 贷款级服务费对账：`portmrcremitloanlevelrecap.total_accrued_earned_servicing_fees` vs `portmonth.servicefee`。 |
| 5 | `mrc_other_check` | **MRC_Adv_Info** | `flow/remit_validation/mrc_validation.py:136-158`（含 helper `_mrc_adv_info_sql` 在 105-133） | 8 | 分桶聚合（`nonrecovcorpadv` / `recovcorpadv` / `escadv`），当月与前月 pandas merge 算 MoM。 |

（字段数来自 `util/gen_remit_validation_report.py:1180-1293` 的 helper 函数 —— `_summary_columns` / `_general_columns("mrc_ln")` / `_advance_columns("mrc_ln")` / `_service_fee_columns("mrc_ln")` / `_adv_info_columns`。）

## 输出 sheet 注册

集中在 `util/gen_remit_validation_report.py:1327-1357` 的一个 `dict.update`：

- `MRC_Summary_check` —— `_summary_columns()`
- `MRC_General_Check` —— `_general_columns("mrc_ln")` + 高亮 diff 列：`intrate_diff_remitvsdaily`、`nextduedate_diff_remitvsdaily`、`begbal_diff_remitvsdaily`、`endbal_diff_remitvsdaily`、`deferredprincipal_diff_remitvsdaily`、`deferredint_diff_remitvsdaily`、`pandi_schedule_diff_remitvsdaily`
- `MRC_Advance_Check` —— `_advance_columns("mrc_ln")` + 高亮：`escadv_diff_remitvsdaily`、`recovcorpadv_diff_remitvsdaily`、`nonrecovcorpadv_diff_remitvsdaily`、`totalcorpadv_diff_remitvsdaily`
- `MRC_ServiceFee_Check` —— `_service_fee_columns("mrc_ln")` + 高亮：`servicefee_diff`
- `MRC_Adv_Info` —— `_adv_info_columns()`

## 源数据表（Redshift）

| Schema.Table | 使用的 validator |
|---|---|
| `port.portmonth` | v1、v2、v3、v4（MRC 的 remit 主表） |
| `port.basic_data_daily_loan_common` | v2、v3（daily 快照，与 remit 对账） |
| `port.basic_data_monthly_loan_common` | v2（计划 P&I 查询） |
| `port.portfunding` | v2、v3、v4（dealid fallback） |
| `mrc.portmrcremitloanlevelrecap` | v4（MRC 专属应计服务费） |
| `mrc.portmrcremit3rdpartyadvances` | v5（第三方 advance 桶） |
| `mrc.portmrcremitcorpadvances` | v5（可回收 corp advance 桶） |
| `mrc.portmrcremitescrowadvances` | v5（escrow advance 桶） |

## 编排接线

`flow/remit_validation/remit_validation.py:134-144` 把 5 个 task 输出存入全局 `VALIDATION_TABLE_MAP`：

```python
VALIDATION_TABLE_MAP['mrc_summary_check']   = mrc_summary_df
VALIDATION_TABLE_MAP['mrc_general_check']   = mrc_general_df
VALIDATION_TABLE_MAP['mrc_adv_check']       = mrc_adv_df
VALIDATION_TABLE_MAP['mrc_service_fee_check'] = mrc_service_fee_df
VALIDATION_TABLE_MAP['mrc_adv_info']        = mrc_adv_info_df
```

键名通过 `util/gen_remit_validation_report.py` 的 `sheet_setting` 注册表（1327 行起）映射到 sheet 名。

## 备注 / 观察

- **v1 (Summary)** 是单行聚合 —— 最简单的 validator；适合作为第一个目标。
- **v5 (Adv_Info)** 是唯一在 SQL 之外用 pandas merge（当月 vs 前月）的 validator —— 需要 Python parity，不只是 SQL parity。同一个 `_mrc_adv_info_sql` 被跑两次（当期 `fctrdt` + 前一期 `fctrdt_1m`）。
- **v2 和 v3** 结构相似（CTE `r`/`p`/`p2` over portmonth + daily 快照），引用的上游表也大体相同 —— 大部分 lineage 抽取工作可复用。
- 未在 MRC 代码路径观察到类似 SLS 的空数据 bug（无 `params=None` 问题）。
- `mrc_ln` 是 MRC servicer 的贷款号，对应 `port.portmonth` 的 `svcloanid` 字段。

## 推荐实施顺序

1. **v1 (Summary)** —— 最小、单行、单表 → 端到端跑通 YAML + harness 闭环，建立信心。
2. **v4 (ServiceFee)** —— 小（9 列），SQL 在 `mrc_validation.py` 内部自包含。
3. **v5 (Adv_Info)** —— 引入 Python merge 这一变数；提前隔离该复杂度。
4. **v2 (General)** —— SQL 最大（~30 列），sqlglot 压力最大的测试。
5. **v3 (Advance)** —— 与 v2 结构相同，v2 跑通后应最快。
