# MRC 汇总校验

**ID**：`mrc/summary_check` &nbsp;&nbsp; **Servicer**：`mrc` &nbsp;&nbsp; **源码出处**：`flow/remit_validation/mrc_validation.py:8`

对当月所有 MRC 贷款的 remit 关键金额做单行聚合汇总，用于核对 servicer 上报的总量是否合理。

## 业务规则

对 port.portmonth 表里 servicer='MRC' 且 fctrdt=当期因子日 的所有行，求和 13 个金额字段
（本金/利息收回、escrow 与 corp advance 变动、服务费、sub-remit 与 total remit、期初与期末余额）。
输出单行，asofdate=remit_date。

!!! info "业务影响"
    若汇总错误，整份 MRC 当月 remit 文件均可疑。

## 产出 sheets

- [MRC_Summary_check](../../sheets/MRC_Summary_check.md) —— 对当月所有 MRC 贷款的 remit 关键金额做单行聚合，用于核对 servicer 上报总量是否合理。


## 源数据表

- `port.portmonth`

*（纯 Python validator，无外部 SQL 文件。）*

**标签**：`mrc`, `summary`, `stub`