# Sheet — MRC_ServiceFee_Check

Loan-level service-fee reconciliation: MRC's loan-level remit recap vs the consolidated
portmonth servicefee. Any non-zero diff flags an aggregation mismatch.


**Producing validators**: [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`fctrdt`](#col-1) | `date` | — | Factor date from portmrcremitloanlevelrecap. |
| 2 | [`loanid`](#col-2) | `string` | — | Internal loan id from portmrcremitloanlevelrecap. |
| 3 | [`mrc_ln`](#col-3) | `string` | — | MRC servicer loan number. |
| 4 | [`dealid`](#col-4) | `string` | — | Deal id, taken from portmonth first; falls back to portfundi… |
| 5 | [`servicefee_remit_raw`](#col-5) | `decimal` | — | total_accrued_earned_servicing_fees from portmrcremitloanlev… |
| 6 | [`servicefee_portmonth`](#col-6) | `decimal` | — | servicefee from port.portmonth (consolidated, MRC). |
| 7 | [`servicefee_diff`](#col-7) | `decimal` | — | servicefee_remit_raw − servicefee_portmonth. Non-zero = aggr… |
| 8 | [`asofdate`](#col-8) | `date` | — | Remit date (set in Python after SQL). |

## Column logic cards


### <a name="col-1"></a>`fctrdt`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): Factor date from portmrcremitloanlevelrecap.

**业务规则 (ZH)**: 来自 portmrcremitloanlevelrecap 的因子日期。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-2"></a>`loanid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): Internal loan id from portmrcremitloanlevelrecap.

**业务规则 (ZH)**: portmrcremitloanlevelrecap 中的内部 loan id。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-3"></a>`mrc_ln`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): MRC servicer loan number.

**业务规则 (ZH)**: MRC servicer 的贷款号。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-4"></a>`dealid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): Deal id, taken from portmonth first; falls back to portfunding.

**业务规则 (ZH)**: Deal id，优先取 portmonth；缺则回退到 portfunding。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-5"></a>`servicefee_remit_raw`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): total_accrued_earned_servicing_fees from portmrcremitloanlevelrecap (loan-level raw).

**业务规则 (ZH)**: portmrcremitloanlevelrecap 的 total_accrued_earned_servicing_fees（贷款级原始值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-6"></a>`servicefee_portmonth`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): servicefee from port.portmonth (consolidated, MRC).

**业务规则 (ZH)**: port.portmonth 的 servicefee（合并后，MRC）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-7"></a>`servicefee_diff`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): servicefee_remit_raw − servicefee_portmonth. Non-zero = aggregation mismatch.

**业务规则 (ZH)**: servicefee_remit_raw − servicefee_portmonth。非零 = 聚合不一致。

!!! info "Business impact"
    Highlighted in the report when non-zero; investigated by ops.

*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-8"></a>`asofdate`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**Business rule** (EN): Remit date (set in Python after SQL).

**业务规则 (ZH)**: Remit 日期（SQL 后在 Python 中赋值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---

