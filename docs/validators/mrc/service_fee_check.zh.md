# MRC 服务费核对

**ID**：`mrc/service_fee_check` &nbsp;&nbsp; **Servicer**：`mrc` &nbsp;&nbsp; **源码出处**：`flow/remit_validation/mrc_validation.py:75`

贷款级服务费对账：把 MRC 的贷款级 remit 明细（portmrcremitloanlevelrecap）与
portmonth 中合并后的 servicefee 字段逐贷比对，发现差异即标记。

## 业务规则

对 mrc.portmrcremitloanlevelrecap 当期 fctrdt 的每一行，左关联 port.portmonth（MRC）
on (fctrdt, loanid)，并左关联 port.portfunding on loanid 取 dealid。输出
servicefee_remit_raw（来自 recap）、servicefee_portmonth 与两者差额。
servicefee_diff 非零即提示聚合不一致。

!!! info "业务影响"
    服务费错误直接影响 servicer 收入确认。

## 产出 sheets

- [MRC_ServiceFee_Check](../../sheets/MRC_ServiceFee_Check.md) —— 贷款级服务费对账：MRC 贷款级 remit 明细 vs portmonth 合并后的 servicefee。
差额非零即提示聚合不一致。


## 源数据表

- `mrc.portmrcremitloanlevelrecap`
- `port.portmonth`
- `port.portfunding`

*（纯 Python validator，无外部 SQL 文件。）*

**标签**：`mrc`, `service_fee`, `stub`