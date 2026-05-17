# Sheet — MRC_Adv_Info

Bucketed advance amounts at the description + transaction_code level for three advance
categories (non-recoverable corp, recoverable corp, escrow), with prior-month MoM ratio.


**Producing validators**: [`mrc/other_check`](../validators/mrc/other_check.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`bucket`](#col-1) | `string` | — | Bucket label: one of 'nonrecovcorpadv', 'recovcorpadv', 'esc… |
| 2 | [`description`](#col-2) | `string` | — | Bucket-specific description column:
• nonrecovcorpadv: portm… |
| 3 | [`transaction_code`](#col-3) | `string` | — | Bucket-specific transaction-code column:
• nonrecovcorpadv /… |
| 4 | [`amt`](#col-4) | `decimal` | — | Current-month bucketed sum:
• corp buckets: sum(coalesce(adv… |
| 5 | [`amt_1m`](#col-5) | `decimal` | — | Prior-month bucketed sum (same formula, prior fctrdt). Null … |
| 6 | [`amt_MoM`](#col-6) | `float` | — | amt / amt_1m − 1 (month-over-month ratio change). |
| 7 | [`asofdate`](#col-7) | `date` | — | Remit date (set in Python after current-month SQL). |

## Column logic cards


### <a name="col-1"></a>`bucket`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Bucket label: one of 'nonrecovcorpadv', 'recovcorpadv', 'escadv'.

**业务规则 (ZH)**: 桶标签：'nonrecovcorpadv' / 'recovcorpadv' / 'escadv' 之一。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*


**Sample values**: `nonrecovcorpadv`, `recovcorpadv`, `escadv`
---


### <a name="col-2"></a>`description`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Bucket-specific description column:
• nonrecovcorpadv: portmrcremit3rdpartyadvances.description
• recovcorpadv:    portmrcremitcorpadvances.reason
• escadv:          portmrcremitescrowadvances.cat


**业务规则 (ZH)**: 按桶取不同字段：
• nonrecovcorpadv：portmrcremit3rdpartyadvances.description
• recovcorpadv：portmrcremitcorpadvances.reason
• escadv：portmrcremitescrowadvances.cat



*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-3"></a>`transaction_code`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Bucket-specific transaction-code column:
• nonrecovcorpadv / recovcorpadv: tran_code
• escadv:                         disbursement_code


**业务规则 (ZH)**: 按桶取不同字段：
• nonrecovcorpadv / recovcorpadv：tran_code
• escadv：disbursement_code



*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-4"></a>`amt`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Current-month bucketed sum:
• corp buckets: sum(coalesce(advances,0) + coalesce(recoveries,0))
• escadv:       sum(total_activity)


**业务规则 (ZH)**: 当期桶求和：
• corp 桶：sum(coalesce(advances,0) + coalesce(recoveries,0))
• escadv：sum(total_activity)



*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-5"></a>`amt_1m`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Prior-month bucketed sum (same formula, prior fctrdt). Null if not joined.

**业务规则 (ZH)**: 前一月桶求和（同公式、前一期 fctrdt）。未匹配则为空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-6"></a>`amt_MoM`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): amt / amt_1m − 1 (month-over-month ratio change).

**业务规则 (ZH)**: amt / amt_1m − 1（环比变化率）。

!!! info "Business impact"
    Large absolute MoM swings prompt ops to investigate.

*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-7"></a>`asofdate`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/other_check`](../validators/mrc/other_check.md) |

**Business rule** (EN): Remit date (set in Python after current-month SQL).

**业务规则 (ZH)**: Remit 日期（当期 SQL 后在 Python 中赋值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---

