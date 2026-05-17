# PrefectFlow Whitebox

欢迎来到 `PrefectFlow` 项目 **remit_validation** 流程的白盒文档站点。

本站点由每个 validator 与每个 sheet 的 YAML metadata **自动生成**。
报表每个 sheet 的每个 column 都有自己的"逻辑卡片"，展示其来源字段、
SQL 表达式、双语业务规则、样例值与上下游 lineage。

## 从哪里开始

- **Validators** —— 代码视角，按 servicer 分组
- **Sheets** —— 报表输出视角；**业务方主要入口**。点击任一 column
  查看完整逻辑
- **Lineage** —— 全量 DAG（dataset + column 双层）
- **Known deltas** —— 与原系统的有意差异 + 业务理由

## 范围

**白盒**：Redshift 数据 → validators → 报表 sheets

**黑盒**（不在本期范围）：vendor 原始文件 → `flow/servicer_data/` 入仓
→ Redshift。未来可能补做。

## Pilot

站点按 **MRC 优先**（5 个 validator）填充。其他 servicer 在 MRC pilot
gate 通过后陆续推进。

---

English version: switch language via top menu → English.
