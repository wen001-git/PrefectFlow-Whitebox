# MRC Advance 明细（第三方 / corp / escrow 桶 MoM）

**ID**：`mrc/other_check` &nbsp;&nbsp; **Servicer**：`mrc` &nbsp;&nbsp; **源码出处**：`flow/remit_validation/mrc_validation.py:136`

对三类 advance（不可回收 corp、可回收 corp、escrow）按 description + 交易代码维度
做分桶聚合，并与前一月做 MoM 比较。运维用来排查异常变动。

## 业务规则

当期与前期 fctrdt 各跑一次三段 UNION 聚合：
(1) nonrecovcorpadv：从 portmrcremit3rdpartyadvances 按 (description, tran_code) 求 sum(advances+recoveries)；
(2) recovcorpadv：从 portmrcremitcorpadvances 按 (reason, tran_code) 求同一指标；
(3) escadv：从 portmrcremitescrowadvances 按 (cat, disbursement_code) 求 sum(total_activity)。
之后在 pandas 中按 (bucket, description, transaction_code) merge 当期与前期，计算
amt_MoM = amt / amt_1m - 1。

!!! info "业务影响"
    MoM 大幅波动促使运维排查异常交易代码。

## 产出 sheets

- [MRC_Adv_Info](../../sheets/MRC_Adv_Info.md) —— 对三类 advance（不可回收 corp、可回收 corp、escrow）按 description + 交易代码维度做
分桶聚合，并与前一月做 MoM 比较。


## 源数据表

- `mrc.portmrcremit3rdpartyadvances`
- `mrc.portmrcremitcorpadvances`
- `mrc.portmrcremitescrowadvances`

*（纯 Python validator，无外部 SQL 文件。）*

**标签**：`mrc`, `advance_detail`, `pandas_merge`, `stub`