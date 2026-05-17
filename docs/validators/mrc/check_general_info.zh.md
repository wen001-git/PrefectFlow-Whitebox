# MRC 一般信息核对（remit vs daily）

**ID**：`mrc/check_general_info` &nbsp;&nbsp; **Servicer**：`mrc` &nbsp;&nbsp; **源码出处**：`flow/remit_validation/servicer_validation_with_portdaily.py:635`

贷款级对账：把关键贷款属性（利率、下次到期日、期初/期末余额、deferred principal/interest、P&I）
在 servicer 上报的 remit 报表（port.portmonth）与内部 daily 快照
（basic_data_daily_loan_common）之间逐贷比对。

## 业务规则

把 MRC 的 portmonth（remit 主表）与 basic_data_daily_loan_common 的两个快照
（上月末 & 当月末）按 loanid 关联。对每笔贷款输出 "_remit" 与 "_daily" 值，以及它们的
"_diff_remitvsdaily" 差异。利率 / 下次到期日 / 余额 / deferred 金额 / P&I schedule 上的
非零差异，提示 servicer 上报可能有误。

!!! info "业务影响"
    差异会进入下游投资人报表对账流程。

## 产出 sheets

- [MRC_General_Check](../../sheets/MRC_General_Check.md) —— 贷款级关键属性对账：servicer remit 报表（port.portmonth）vs 内部 daily 快照
（basic_data_daily_loan_common）。"_remit" 与 "_daily" 配对加 "_diff_remitvsdaily"
差异，标记 servicer 上报可能的错误。


## 源数据表

- `port.portmonth`
- `port.basic_data_daily_loan_common`
- `port.basic_data_monthly_loan_common`
- `port.portfunding`

*（纯 Python validator，无外部 SQL 文件。）*

**标签**：`mrc`, `general`, `remit_vs_daily`, `stub`