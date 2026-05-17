# Sheets

自动生成索引。点击任一 sheet 进入，再点击任一 column 查看完整逻辑。

- [MRC_Adv_Info](MRC_Adv_Info.md) —— 对三类 advance（不可回收 corp、可回收 corp、escrow）按 description + 交易代码维度做
分桶聚合，并与前一月做 MoM 比较。

- [MRC_Advance_Check](MRC_Advance_Check.md) —— MRC 贷款级 advance 余额对账。每笔贷款：escrow / 可回收 corp / 不可回收 corp advance
在 remit（portmonth _chg 字段）与 daily 快照（当月末 - 上月末）之间比对。
"_diff_remitvsdaily" 非零 = servicer 上报可能有问题。

- [MRC_General_Check](MRC_General_Check.md) —— 贷款级关键属性对账：servicer remit 报表（port.portmonth）vs 内部 daily 快照
（basic_data_daily_loan_common）。"_remit" 与 "_daily" 配对加 "_diff_remitvsdaily"
差异，标记 servicer 上报可能的错误。

- [MRC_ServiceFee_Check](MRC_ServiceFee_Check.md) —— 贷款级服务费对账：MRC 贷款级 remit 明细 vs portmonth 合并后的 servicefee。
差额非零即提示聚合不一致。

- [MRC_Summary_check](MRC_Summary_check.md) —— 对当月所有 MRC 贷款的 remit 关键金额做单行聚合，用于核对 servicer 上报总量是否合理。

- [placeholder_hello](placeholder_hello.md) —— 自检 sheet —— 占位贷款的本金翻倍结果。
