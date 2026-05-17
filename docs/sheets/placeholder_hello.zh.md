# Sheet —— placeholder_hello

自检 sheet —— 占位贷款的本金翻倍结果。

**产出该 sheet 的 validators**：[`_placeholder/hello`](../validators/_placeholder/hello.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`loan_id`](#col-1) | `string` | `placeholder_input.loan_id` | 贷款 ID，从源表拷贝。 |
| 2 | [`principal_x2`](#col-2) | `decimal` | `placeholder_input.principal` | 本金乘以 2（仅用于自检计算）。 |

## 字段逻辑卡片


### <a name="col-1"></a>`loan_id`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`_placeholder/hello`](../validators/_placeholder/hello.md) |

**业务规则（中文）**：贷款 ID，从源表拷贝。

**Business rule (EN)**: Loan identifier, copied from source.


**来源**（列级 lineage，由 sqlglot 自动抽取）：

| 上游表 | 上游字段 | 变换 |
|---|---|---|
| `placeholder_input` | `loan_id` | — |

**表达式**：

```sql
placeholder_input.loan_id AS loan_id
```

**样例值**：`L001`, `L002`
---


### <a name="col-2"></a>`principal_x2`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`_placeholder/hello`](../validators/_placeholder/hello.md) |

**业务规则（中文）**：本金乘以 2（仅用于自检计算）。

**Business rule (EN)**: Principal doubled (selftest computation only).

!!! info "业务影响"
    仅自检使用；无业务影响。

**来源**（列级 lineage，由 sqlglot 自动抽取）：

| 上游表 | 上游字段 | 变换 |
|---|---|---|
| `placeholder_input` | `principal` | — |

**表达式**：

```sql
placeholder_input.principal * 2 AS principal_x2
```

**样例值**：`200000`, `350000`
---

