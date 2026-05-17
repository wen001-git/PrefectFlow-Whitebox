# Sheet —— MRC_Adv_Info

对三类 advance（不可回收 corp、可回收 corp、escrow）按 description + 交易代码维度做
分桶聚合，并与前一月做 MoM 比较。


**产出该 sheet 的 validators**：[`mrc/other_check`](../validators/mrc/other_check.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`bucket`](#col-1) | `string` | — | 桶标签：'nonrecovcorpadv' / 'recov… |
| 2 | [`description`](#col-2) | `string` | — | 按桶取不同字段：
• nonrecovcorpadv：por… |
| 3 | [`transaction_code`](#col-3) | `string` | — | 按桶取不同字段：
• nonrecovcorpadv / r… |
| 4 | [`amt`](#col-4) | `decimal` | — | 当期桶求和：
• corp 桶：sum(coalesce(a… |
| 5 | [`amt_1m`](#col-5) | `decimal` | — | 前一月桶求和（同公式、前一期 fctrdt）。未匹配则为空。 |
| 6 | [`amt_MoM`](#col-6) | `float` | — | amt / amt_1m − 1（环比变化率）。 |
| 7 | [`asofdate`](#col-7) | `date` | — | Remit 日期（当期 SQL 后在 Python 中赋值）… |

## 字段逻辑卡片


### <a name="col-1"></a>`bucket`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：桶标签：'nonrecovcorpadv' / 'recovcorpadv' / 'escadv' 之一。

**Business rule (EN)**: Bucket label: one of 'nonrecovcorpadv', 'recovcorpadv', 'escadv'.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*


**样例值**：`nonrecovcorpadv`, `recovcorpadv`, `escadv`
---


### <a name="col-2"></a>`description`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：按桶取不同字段：
• nonrecovcorpadv：portmrcremit3rdpartyadvances.description
• recovcorpadv：portmrcremitcorpadvances.reason
• escadv：portmrcremitescrowadvances.cat


**Business rule (EN)**: Bucket-specific description column:
• nonrecovcorpadv: portmrcremit3rdpartyadvances.description
• recovcorpadv:    portmrcremitcorpadvances.reason
• escadv:          portmrcremitescrowadvances.cat



*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-3"></a>`transaction_code`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：按桶取不同字段：
• nonrecovcorpadv / recovcorpadv：tran_code
• escadv：disbursement_code


**Business rule (EN)**: Bucket-specific transaction-code column:
• nonrecovcorpadv / recovcorpadv: tran_code
• escadv:                         disbursement_code



*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-4"></a>`amt`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：当期桶求和：
• corp 桶：sum(coalesce(advances,0) + coalesce(recoveries,0))
• escadv：sum(total_activity)


**Business rule (EN)**: Current-month bucketed sum:
• corp buckets: sum(coalesce(advances,0) + coalesce(recoveries,0))
• escadv:       sum(total_activity)



*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-5"></a>`amt_1m`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：前一月桶求和（同公式、前一期 fctrdt）。未匹配则为空。

**Business rule (EN)**: Prior-month bucketed sum (same formula, prior fctrdt). Null if not joined.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-6"></a>`amt_MoM`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：amt / amt_1m − 1（环比变化率）。

**Business rule (EN)**: amt / amt_1m − 1 (month-over-month ratio change).

!!! info "业务影响"
    MoM 绝对值过大触发运维排查。

*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-7"></a>`asofdate`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**业务规则（中文）**：Remit 日期（当期 SQL 后在 Python 中赋值）。

**Business rule (EN)**: Remit date (set in Python after current-month SQL).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---

