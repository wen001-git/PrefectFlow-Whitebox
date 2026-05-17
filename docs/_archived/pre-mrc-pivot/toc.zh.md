# Validation Report 计算逻辑文档 —— TOC（阶段 1 第 1 步交付物）

> 本 TOC 是**阶段 1 的入口交付物**。其作用是先把整份逻辑文档要写哪些章节、覆盖
> 哪些 servicer、覆盖哪些 sheet、每个 sheet 要写到什么深度，**全部列清楚交由用户审阅**。
>
> 用户 approve 本 TOC 后，才会按 `1.1 → 1.2 → 1.3 → 1.4` 顺序逐章节展开。
>
> **本 TOC 不写任何新系统设计、不做技术选型、不写新代码。** 全部内容只反推
> `C:\Users\jli\MyData\Copilot\PrefectFlow` 现有源码的真实行为。

英文版见 / English version: `toc.en.md`（使用站点顶栏的语言切换器）

---

## 反推依据（源码 ground truth）

本 TOC 的所有 servicer / sheet 清单都从下列源码直接抽取，可逐行追溯：

- 入口 flow：`flow/remit_validation/remit_validation.py`（180 行）
  - `@flow remit_validation_check` 函数（line 66-177）按固定顺序调用 7 个 servicer 的 validator + 8 个 scattered cross-servicer validator，把结果塞进 `VALIDATION_TABLE_MAP` 后调 `gen_remit_report` 输出 XLSX。
- sheet 注册：`util/gen_remit_validation_report.py`
  - 顶层 `setting["sheet_setting"]` dict（line 87-1162）注册 SLS / Carrington / Shellpoint / Arvest / CC5 / scattered 共 30 个 sheet。
  - `setting["sheet_setting"].update({...})`（line 1296-1357）追加 Selene 5 + MRC 5 共 10 个 sheet。
  - sheet 列定义辅助函数：`_summary_columns` / `_general_columns` / `_advance_columns` / `_service_fee_columns` / `_adv_info_columns`（line 1180-1294）。
- 每个 servicer 的 validator 实现文件：`flow/remit_validation/<servicer>_validation.py` 与对应 `_db.py`。
- 跨 servicer 校验：`flow/remit_validation/scattered_validation.py`。
- 共享 SQL：`flow/remit_validation/servicer_validation_with_portdaily.py`。

---

## Validation Report 全貌（最终 XLSX 共 40 个 sheet）

来源：`gen_remit_report` 在 `remit_validation.py:165-175` 接收 40 个 DataFrame，依次写入下列 sheet。

| # | Sheet 名 | 归属 | 数据来源 DataFrame | 产出函数 |
|---|---|---|---|---|
| 1 | `SLS_Summary_check`        | SLS    | （当前 `None`） | `sls_summary_check`（定义但 flow 未调用） |
| 2 | `SLS_Advance_Check`        | SLS    | （当前 `None`） | `sls_validation_check` |
| 3 | `SLS_General_Check`        | SLS    | （当前 `None`） | `sls_general_check` |
| 4 | `SLS_ServiceFee_Check`     | SLS    | （当前 `None`） | `sls_check_service_fee` |
| 5 | `SLS_Other_Check`          | SLS    | （当前 `None`） | `sls_other_fee` |
| 6 | `Carrington_Summary_check` | Carrington | `carrington_summary_df` | `carrington_summary_check` |
| 7 | `Carrington_General_Check` | Carrington | `carrington_general_df` | `carrington_general_info_check` |
| 8 | `Carrington_Advance_Check` | Carrington | `carrington_adv_df` | `carrington_new_adv_check` |
| 9 | `Carrington_ServiceFee_Check` | Carrington | `carrington_service_fee` | `carrington_service_fee_check` |
| 10 | `Carrington_Adv_Info`     | Carrington | `carrington_adv_info`（`carrington_other_check` 第二返回） | `carrington_other_check` |
| 11 | `Carrington_Trans_Info`   | Carrington | `trans_df`（`carrington_other_check` 第一返回） | `carrington_other_check` |
| 12 | `Shellpoint_Summary_check`   | Shellpoint | `shellpoint_summary_df` | `shellpoint_summary_check` |
| 13 | `Shellpoint_General_Check`   | Shellpoint | `s_general_df` | `shellpoint_check_general_info` |
| 14 | `Shellpoint_Advance_Check`   | Shellpoint | `s_adv_df`     | `shellpoint_check_avd_balance` |
| 15 | `Shellpoint_ServiceFee_Check`| Shellpoint | `shellpoint_service_fee` | `shellpoint_service_fee_check` |
| 16 | `Shellpoint_Adv_Info`        | Shellpoint | `shellpoint_adv_info` | `shellpoint_other_check` |
| 17 | `Arvest_Sum_remit`         | Arvest | `sum_remit_df` | `arvest_get_sub_and_tot_remit` |
| 18 | `Arvest_Bal_Chg_check`     | Arvest | `arvest_bal_chg_df` | `arvest_compare_bal_chg` |
| 19 | `Arvest_PandI_check`       | Arvest | `arvest_pandi_compare_df` | `arvest_pandi_info_check` |
| 20 | `Arvest_ServiceFee_check`  | Arvest | `arvest_service_fee_df` | `arvest_service_fee_check` |
| 21 | `Cc5_ServiceFee_check`     | CC5 | `cc5_service_fee_check_df` | `cc5_service_fee_check` |
| 22 | `Cc5_bal_check`            | CC5 | `cc5_bal_check_df` | `cc5_principal_bal_check` |
| 23 | `Month_vs_Funding`         | Scattered | `month_vs_funding` | `adv_month_vs_funding` |
| 24 | `PandI_vs_NextDueDate`     | Scattered | `pandi_vs_nextdue_date` | `check_pandi_nextduedate_logic` |
| 25 | `Service Fee All`          | Scattered | `service_fee_all` | `all_servicer_fee_check` |
| 26 | `Paid-off Loans Check`     | Scattered | `paid_off_loans` | `check_paid_off_loans` |
| 27 | `Mod_loans_info`           | Scattered | `modi_loan_info` | `check_modi_loan_info` |
| 28 | `Loan_Scale_info`          | Scattered | `loans_scale_info` | `check_loans_scale_info` |
| 29 | `PandI_check`              | Scattered | `pandi_compare_df` | `compare_pandi` |
| 30 | `Paidoff_deffer_check`     | Scattered | `paidoff_loans_deffer_df` | `check_paidoff_loans_deffer` |
| 31 | `Selene_Summary_check`     | Selene | `selene_summary_df` | `selene_summary_check` |
| 32 | `Selene_General_Check`     | Selene | `selene_general_df` | `selene_check_general_info` |
| 33 | `Selene_Advance_Check`     | Selene | `selene_adv_df`     | `selene_check_adv_balance` |
| 34 | `Selene_ServiceFee_Check`  | Selene | `selene_service_fee_df` | `selene_service_fee_check` |
| 35 | `Selene_Adv_Info`          | Selene | `selene_adv_info_df` | `selene_other_check` |
| 36 | `MRC_Summary_check`        | MRC | `mrc_summary_df` | `mrc_summary_check` |
| 37 | `MRC_General_Check`        | MRC | `mrc_general_df` | `mrc_check_general_info` |
| 38 | `MRC_Advance_Check`        | MRC | `mrc_adv_df`     | `mrc_check_adv_balance` |
| 39 | `MRC_ServiceFee_Check`     | MRC | `mrc_service_fee_df` | `mrc_service_fee_check` |
| 40 | `MRC_Adv_Info`             | MRC | `mrc_adv_info_df` | `mrc_other_check` |

⚠️ **SLS 现状说明（已在 `remit_validation.py` 源码核实）**：line 66-177 的 flow 中**没有任何 SLS validator 调用**，
即使 `sls_validation.py` 里定义了 5 个 validator 函数（line 27-29 import）。`gen_remit_report` 调用时这 5 个位置传的是 5 个 `None`（line 166），所以 2026-04-30 gold XLSX 的 SLS 5 个 sheet 都是空表头。阶段 1 的 `1.2.7 SLS` 章节会专门记录这件事 + 复原 SLS validator 设计意图 vs 当前 flow 没接的 gap。

---

## 文档目录（阶段 1 全量章节清单）

按用户 prompt #19 要求，阶段 1 输出的文档覆盖 4 个维度。所有内容由"现有源码反推"，
**不引入任何新系统的概念 / 不做技术建议**。

### 1.1 `overall-flow.zh.md` —— Validation Report 整体生成流程

子章节：

- 1.1.1 触发入口（`@flow remit_validation_check`、`remit_date` / `email` / `to_new_redshift` / `to_mysql` 4 个参数的含义与默认值推导逻辑）
- 1.1.2 数据来源全景：Redshift 上各 servicer 的 raw schema / unified 表 / portfolio daily 表
- 1.1.3 中间 DataFrame / `VALIDATION_TABLE_MAP` 全列表（30 个 key 的含义、写入时机）
- 1.1.4 关键 Python 文件清单（按调用图列出，含每个文件的角色）
- 1.1.5 关键 SQL 文件 / SQL 块清单（`servicer_validation_with_portdaily.py` 等）
- 1.1.6 最终输出 XLSX：路径规则（`VALIDATION_REPORT_ROUTE + date_path + ...`）、40 sheet 的物理写入顺序、`gen_remit_report` 的写入流程
- 1.1.7 调用时序图（Mermaid sequence diagram，从 flow 启动到 XLSX 落盘）

### 1.2 各 Servicer 章节（按 flow 真实调用顺序）

每个 servicer 章节内部统一 4 个维度：
**(a) servicer 总览** —— DB class、validator 文件、入参、依赖的 Redshift 表清单、本 servicer 产出哪几个 sheet。
**(b) 各 sheet 详细生成逻辑** —— 对**每一个** sheet 写：sheet name、对应函数 / SQL / DataFrame、使用的数据源、join key、filter 条件、group by 逻辑、计算字段、校验规则、pass / fail / exception 判断逻辑。
**(c) 字段级计算逻辑** —— 对**每一列** output column 写：source table / source field、transformation logic、calculation formula、business meaning、known edge cases。
**(d) 本 servicer 的数据流分支** —— Mermaid lineage 图：raw vendor → raw schema → Redshift unified → validation query → 本 servicer 的若干 sheet。

按 `remit_validation_check` 真实调用顺序列章节：

- 1.2.1 **Carrington**（6 sheet：Summary / General / Advance / ServiceFee / Adv_Info / Trans_Info）
  - 源：`carrington_validation.py` + `carrington_db.py`；validator 5 个，其中 `carrington_other_check` 返回二元组对应 2 个 sheet。
- 1.2.2 **Shellpoint**（5 sheet：Summary / General / Advance / ServiceFee / Adv_Info）
  - 源：`shellpoint_validation.py` + `shellpoint_db.py`；validator 5 个。
- 1.2.3 **Arvest**（4 sheet：Sum_remit / Bal_Chg_check / PandI_check / ServiceFee_check）
  - 源：`arvest_validation.py` + `arvest_db.py`；validator 4 个。
- 1.2.4 **CC5**（2 sheet：ServiceFee_check / bal_check）
  - 源：`cc5_validation.py` + `cc5_db.py`；validator 2 个。
- 1.2.5 **Selene**（5 sheet：Summary / General / Advance / ServiceFee / Adv_Info）
  - 源：`selene_validation.py` + `selene_db.py`；validator 5 个。
- 1.2.6 **MRC**（5 sheet：Summary / General / Advance / ServiceFee / Adv_Info）
  - 源：`mrc_validation.py` + `mrc_db.py`；validator 5 个。
- 1.2.7 **SLS**（5 sheet，当前为空）
  - 源：`sls_validation.py` + `sls_db.py`；validator 5 个**已定义但 flow 未调用**。
  - 本章须如实记录：定义意图、`gen_remit_report` 接收 5 个 `None` 的事实、空 sheet 输出现象、可考据的历史原因（若 git log / 注释中能找到）。

### 1.3 跨 servicer 章节

- 1.3.1 **Scattered cross-servicer validators**（8 sheet）
  - 源：`scattered_validation.py`
  - 8 个 validator：`adv_month_vs_funding / check_pandi_nextduedate_logic / all_servicer_fee_check / check_paid_off_loans / check_modi_loan_info / check_loans_scale_info / compare_pandi / check_paidoff_loans_deffer`
  - 使用与各 servicer 章节相同的 4 维结构（总览 + 各 sheet + 各字段 + 数据流分支）。

### 1.4 `dataflow.zh.md` —— 跨 servicer 数据流全景

- 1.4.1 raw vendor file（servicer 上游文件）→ raw schema table（`servicer_data` 入仓后的 Redshift 表）的 lineage：本节只列每个 servicer 对应哪些 raw schema 表，不展开 ETL（用户已确认该段算黑盒）。
- 1.4.2 raw schema table → Redshift unified table（portfolio daily / `*_ln` 等汇总表）的口径。
- 1.4.3 unified table → validation query → 各 sheet 的 column-level lineage 汇总（Mermaid 全图）。
- 1.4.4 cross-servicer 流（如 `Service Fee All` 同时读多个 servicer 中间表的关系图）。
- 1.4.5 整张 Validation Report 数据流总览图。

### 1.5 用户走查（gate，必须用户明确 approve 才算 done）

- 1.5.1 用户在 mkdocs 站点 / 直接 markdown 通读 1.1 ~ 1.4 全部内容。
- 1.5.2 用户在 `decisions.md` 记录走查反馈（覆盖度 / 准确度 / 业务可读性）。
- 1.5.3 用户写 "stage 1 approved" 后，阶段 2 才能解锁。

---

## 不在本 TOC 范围内（再次提醒）

- ❌ 不讨论新系统功能、架构、技术选型（FastAPI / Streamlit / Dagster / DBT 等一律不提）。
- ❌ 不写任何 Python / SQL 新代码。
- ❌ 不重写既有 validator。
- ❌ 不做 snapshot / diff harness（属于已冻结基础设施，阶段 1 用不到）。
- ❌ 不修 PrefectFlow 源仓库（只读）。

阶段 2（feature list / SRS / pages / data model / API / dev plan / test plan / phased impl）
**必须**等 1.5 `stage1-review` 用户 approve 后才解锁。

---

## 待用户决定的开放项

请在 approve 本 TOC 前回复下列任一选择（也可全部用默认）：

1. **章节先后**：默认按 1.2.1 → 1.2.7 顺序写。是否需要调整？（如想先看 MRC 完整样例做 schema 检验，可把 1.2.6 MRC 提到 1.2.1。）
2. **字段级粒度**：默认每个 column 列出 source / transform / formula / business meaning / edge cases 5 项。是否再加项（如：示例数据值、上游 raw field 名称、可能的 NULL 行为）？
3. **双语形式**：✅ 已确认 —— 中文 `.zh.md` 与英文 `.en.md` 两份分开。
4. **scattered sheet 命名 "Service Fee All" / "Paid-off Loans Check" 含空格**：保留源码原名（推荐，保真）还是文档里统一改成 underscore？
