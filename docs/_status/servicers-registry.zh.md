# 项目状态 · Servicers Registry (zh)

> **Purpose**: PrefectFlow-Whitebox 反向工程进度的**唯一可信视图**。任何 servicer
> 状态变化（从 ⏳ → 🚧 → ✅），必须同步更新本文件、`plan.md` 中的对应行、SQL todo
> 状态，以及（阶段 2 后）validator registry 工具输出。
>
> **Intended audience**: 当前 session agent、下一次 session 接手 agent、用户。
> 任何人想知道"我们做到哪儿了"、"还有什么没分析"，先看这一张表。
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — 创建。v9.1 placeholder-everywhere 规则落地。 |

---

## 图例 / Legend

| 标记 | 含义 |
|---|---|
| ✅ | 已完成（done） |
| 🚧 | 进行中（in progress） |
| ⏳ | 已预留 placeholder，待分析（pending-deferred） |
| ⛔ | 尚未启动（not started） |
| 🔒 | 已冻结，不再适用（frozen） |

---

## Servicer 分析状态矩阵 / Servicer status matrix

> 源真理（source of truth）：本表。`plan.md` 的同名表与本表必须一致。

| Servicer | Sheets | Stage 1 文档 | Stage 2 系统 | 上次分析 | 下一步责任 | 已知空白 / 假设 |
|---|---|---|---|---|---|---|
| **MRC** | 5 | 🚧 进行中（v9.1 起活跃） | ⏳ 等 Stage 1 review | 2026-05-15（冻结 pilot scope.md） | 当前 session | 全量重新分析中 |
| **Carrington** | 6 | ✅ 章节完成（2026-05-17，已归档至 `_archived/pre-mrc-pivot/`） | ⛔ 未启动 | 2026-05-17 | 未来 session | MRC 系统定型后可能需要刷新模板 |
| **Shellpoint** | 5 | ✅ 章节完成（2026-05-17，已归档） | ⛔ 未启动 | 2026-05-17 | 未来 session | 同 Carrington |
| **Arvest** | 4（假设） | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | sheet 数假设 4，需对照 `arvest_validation.py` 核实；SQL 模板未验证 |
| **CC5** | 2 | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | 最小 servicer；未来回归热身首选 |
| **Selene** | 5（假设） | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | sheet 数假设 5，需核实 |
| **SLS** | 5（假设） | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | **已知问题：2026-04 空数据 bug**，分析时必须记录 |
| **Scattered**（跨 servicer，~8 个 validator） | n/a | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | 8 个 validator 清单尚未枚举 |
| **跨 servicer dataflow / lineage** | n/a | ⏳ 仅 placeholder | ⛔ 未启动 | 从未 | 未来 session | 需所有 per-servicer 文档完成后才能整合 |

---

## Placeholder 位置索引 / Placeholder index

对每个 `⏳ pending` servicer，以下 placeholder 必须已就位：

| Servicer | Stage 1 stub | Stage 2 ingestion stub | Stage 2 handler stub | Lineage 分支 |
|---|---|---|---|---|
| Arvest    | [`docs/arvest/_pending.zh.md`](../arvest/_pending.zh.md)       | 待 Stage 2 创建 | 待 Stage 2 创建 | 待 Stage 2 创建（dashed） |
| CC5       | [`docs/cc5/_pending.zh.md`](../cc5/_pending.zh.md)             | 待 Stage 2 创建 | 待 Stage 2 创建 | 待 Stage 2 创建（dashed） |
| Selene    | [`docs/selene/_pending.zh.md`](../selene/_pending.zh.md)       | 待 Stage 2 创建 | 待 Stage 2 创建 | 待 Stage 2 创建（dashed） |
| SLS       | [`docs/sls/_pending.zh.md`](../sls/_pending.zh.md)             | 待 Stage 2 创建 | 待 Stage 2 创建 | 待 Stage 2 创建（dashed） |
| Scattered | [`docs/scattered/_pending.zh.md`](../scattered/_pending.zh.md) | 待 Stage 2 创建 | 待 Stage 2 创建 | 待 Stage 2 创建（dashed） |
| Dataflow  | [`docs/dataflow/_pending.zh.md`](../dataflow/_pending.zh.md)   | 待 Stage 2 创建 | n/a | 待 Stage 2 创建（dashed） |

---

## 维护规则 / Maintenance rule

任何 servicer 状态变化（章节交付、todo 更新、新发现的 gap）必须在**同一 commit**
内更新：

1. 本文件（zh + en）
2. `plan.md` 服务者状态矩阵
3. 对应 SQL todo 状态
4. （Stage 2 后）validator registry 工具输出

见 AGENTS.md § 6.8。
