# Sheet — placeholder_hello

Selftest sheet — doubled principals for placeholder loans.

**Producing validators**: [`_placeholder/hello`](../validators/_placeholder/hello.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`loan_id`](#col-1) | `string` | `placeholder_input.loan_id` | Loan identifier, copied from source. |
| 2 | [`principal_x2`](#col-2) | `decimal` | `placeholder_input.principal` | Principal doubled (selftest computation only). |

## Column logic cards


### <a name="col-1"></a>`loan_id`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`_placeholder/hello`](../validators/_placeholder/hello.md) |

**Business rule** (EN): Loan identifier, copied from source.

**业务规则 (ZH)**: 贷款 ID，从源表拷贝。


**Sources** (column-level lineage, auto-extracted via sqlglot):

| Upstream table | Upstream column | Transform |
|---|---|---|
| `placeholder_input` | `loan_id` | — |

**Expression**:

```sql
placeholder_input.loan_id AS loan_id
```

**Sample values**: `L001`, `L002`
---


### <a name="col-2"></a>`principal_x2`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`_placeholder/hello`](../validators/_placeholder/hello.md) |

**Business rule** (EN): Principal doubled (selftest computation only).

**业务规则 (ZH)**: 本金乘以 2（仅用于自检计算）。

!!! info "Business impact"
    Selftest only; no business impact.

**Sources** (column-level lineage, auto-extracted via sqlglot):

| Upstream table | Upstream column | Transform |
|---|---|---|
| `placeholder_input` | `principal` | — |

**Expression**:

```sql
placeholder_input.principal * 2 AS principal_x2
```

**Sample values**: `200000`, `350000`
---

