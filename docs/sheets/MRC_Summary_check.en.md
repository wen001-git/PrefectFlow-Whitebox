# Sheet — MRC_Summary_check

Single-row aggregate of all MRC loans' remit-month financials for sanity-checking the
total volume reported by the servicer.


**Producing validators**: [`mrc/summary_check`](../validators/mrc/summary_check.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`principalreceived`](#col-1) | `decimal` | — | Sum of principalreceived across all MRC loans for the curren… |
| 2 | [`interestreceived`](#col-2) | `decimal` | — | Sum of interestreceived across all MRC loans for the current… |
| 3 | [`escrowadv_chg`](#col-3) | `decimal` | — | Sum of escrowadv_chg (escrow advance change) across all MRC … |
| 4 | [`corpadvrec_chg`](#col-4) | `decimal` | — | Sum of recoverable corp advance change (corpadvrec_chg). |
| 5 | [`corpadvnonrec_chg`](#col-5) | `decimal` | — | Sum of non-recoverable corp advance change (corpadvnonrec_ch… |
| 6 | [`corpadvtotal_chg`](#col-6) | `decimal` | — | Sum of total corp advance change (recoverable + non-recovera… |
| 7 | [`servicefee`](#col-7) | `decimal` | — | Sum of base service fee across all MRC loans. |
| 8 | [`otherfees`](#col-8) | `decimal` | — | Sum of other fees across all MRC loans. |
| 9 | [`totalservicefee`](#col-9) | `decimal` | — | Sum of servicefee + otherfees across all MRC loans. |
| 10 | [`subremit`](#col-10) | `decimal` | — | Sum of subremit across all MRC loans. |
| 11 | [`totremit`](#col-11) | `decimal` | — | Sum of totremit across all MRC loans. |
| 12 | [`beginningbalance`](#col-12) | `decimal` | — | Sum of prevbal (beginning balance) across all MRC loans. |
| 13 | [`endingbalance`](#col-13) | `decimal` | — | Sum of balance (ending balance) across all MRC loans. |
| 14 | [`asofdate`](#col-14) | `date` | — | Remit date (set in Python after aggregation). |

## Column logic cards


### <a name="col-1"></a>`principalreceived`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of principalreceived across all MRC loans for the current fctrdt.

**业务规则 (ZH)**: 当期 fctrdt 所有 MRC 贷款 principalreceived 的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-2"></a>`interestreceived`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of interestreceived across all MRC loans for the current fctrdt.

**业务规则 (ZH)**: 当期 fctrdt 所有 MRC 贷款 interestreceived 的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-3"></a>`escrowadv_chg`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of escrowadv_chg (escrow advance change) across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 escrowadv_chg（escrow advance 变动）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-4"></a>`corpadvrec_chg`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of recoverable corp advance change (corpadvrec_chg).

**业务规则 (ZH)**: 可回收 corp advance 变动（corpadvrec_chg）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-5"></a>`corpadvnonrec_chg`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of non-recoverable corp advance change (corpadvnonrec_chg).

**业务规则 (ZH)**: 不可回收 corp advance 变动（corpadvnonrec_chg）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-6"></a>`corpadvtotal_chg`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of total corp advance change (recoverable + non-recoverable).

**业务规则 (ZH)**: 全部 corp advance 变动（可回收 + 不可回收）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-7"></a>`servicefee`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of base service fee across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款基础服务费的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-8"></a>`otherfees`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of other fees across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款其他费用的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-9"></a>`totalservicefee`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of servicefee + otherfees across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 servicefee + otherfees 的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-10"></a>`subremit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of subremit across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 subremit 的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-11"></a>`totremit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of totremit across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 totremit 的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-12"></a>`beginningbalance`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of prevbal (beginning balance) across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 prevbal（期初余额）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-13"></a>`endingbalance`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Sum of balance (ending balance) across all MRC loans.

**业务规则 (ZH)**: 所有 MRC 贷款 balance（期末余额）的总和。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-14"></a>`asofdate`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**Business rule** (EN): Remit date (set in Python after aggregation).

**业务规则 (ZH)**: Remit 日期（聚合后在 Python 中赋值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---

