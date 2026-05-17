# MRC Advance 余额核对（remit vs daily）

**ID**：`mrc/check_adv_balance` &nbsp;&nbsp; **Servicer**：`mrc` &nbsp;&nbsp; **源码出处**：`flow/remit_validation/servicer_validation_with_portdaily.py:583`

贷款级 advance 余额对账：对每笔 MRC 贷款，把 escrow advance、可回收 corp advance、
不可回收 corp advance 的余额变动在 remit（portmonth 的 _chg 字段）与 daily 快照
（上月末 → 当月末差额）之间比对。

## 业务规则

把 MRC 的 portmonth（remit）与 basic_data_daily_loan_common 的上月末 + 当月末两份
快照按 loanid 关联。对每笔贷款计算 daily 快照差额（curr - prev）—— escrow / 可回收
corp / 不可回收 corp advance 余额，与 servicer 上报的 _chg 字段比对。两边一致时
"_diff_remitvsdaily" 应接近 0。

!!! info "业务影响"
    Advance 不一致会直接影响投资人现金流预测。

## 产出 sheets

- [MRC_Advance_Check](../../sheets/MRC_Advance_Check.md) —— MRC 贷款级 advance 余额对账。每笔贷款：escrow / 可回收 corp / 不可回收 corp advance
在 remit（portmonth _chg 字段）与 daily 快照（当月末 - 上月末）之间比对。
"_diff_remitvsdaily" 非零 = servicer 上报可能有问题。


## 源数据表

- `port.portmonth`
- `port.basic_data_daily_loan_common`
- `port.portfunding`

*（纯 Python validator，无外部 SQL 文件。）*

**标签**：`mrc`, `advance`, `remit_vs_daily`, `stub`