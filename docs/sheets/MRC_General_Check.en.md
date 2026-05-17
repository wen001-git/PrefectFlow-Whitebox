# Sheet — MRC_General_Check

Loan-level reconciliation of key loan attributes between the servicer's remit report
(port.portmonth) and our internal daily snapshot (basic_data_daily_loan_common).
"_remit" and "_daily" pairs with their "_diff_remitvsdaily" deltas flag servicer
reporting errors.


**Producing validators**: [`mrc/check_general_info`](../validators/mrc/check_general_info.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`loanid`](#col-1) | `string` | — | Internal loan id (join key). |
| 2 | [`mrc_ln`](#col-2) | `string` | — | MRC servicer loan number (svcloanid from portmonth). |
| 3 | [`dealid`](#col-3) | `string` | — | Deal id; portmonth first, falls back to portfunding. |
| 4 | [`intrate_remit`](#col-4) | `float` | — | Interest rate as reported by servicer (portmonth.intrate). |
| 5 | [`intrate_daily`](#col-5) | `float` | — | Interest rate in daily snapshot (basic_data_daily_loan_commo… |
| 6 | [`intrate_diff_remitvsdaily`](#col-6) | `float` | — | intrate_remit − intrate_daily. Non-zero highlighted. |
| 7 | [`nextduedate_remit`](#col-7) | `date` | — | Next due date as reported (portmonth.nextduedate). |
| 8 | [`nextduedate_daily`](#col-8) | `date` | — | Next due date in daily snapshot (current month-end). |
| 9 | [`nextduedate_diff_remitvsdaily`](#col-9) | `float` | — | 0 if dates match, 1 if they differ. Non-zero highlighted. |
| 10 | [`begbal_remit`](#col-10) | `decimal` | — | Beginning balance as reported (portmonth.prevbal). |
| 11 | [`begbal_daily`](#col-11) | `decimal` | — | Beginning balance from daily snapshot (prior month-end princ… |
| 12 | [`begbal_diff_remitvsdaily`](#col-12) | `decimal` | — | begbal_remit − begbal_daily. Non-zero highlighted. |
| 13 | [`endbal_remit`](#col-13) | `decimal` | — | Ending balance as reported (portmonth.balance). |
| 14 | [`endbal_daily`](#col-14) | `decimal` | — | Ending balance from daily snapshot (current month-end princi… |
| 15 | [`endbal_diff_remitvsdaily`](#col-15) | `decimal` | — | endbal_remit − endbal_daily. Non-zero highlighted. |
| 16 | [`principal_remit`](#col-16) | `decimal` | — | Principal received per servicer (portmonth.principalreceived… |
| 17 | [`interest_remit`](#col-17) | `decimal` | — | Interest received per servicer (portmonth.interestreceived). |
| 18 | [`prin_bal_diff_remit`](#col-18) | `decimal` | — | prevbal − balance − principalreceived (should be ~0 for a cl… |
| 19 | [`deferredprincipal_remit`](#col-19) | `decimal` | — | Deferred principal as reported (portmonth.deferredprin). |
| 20 | [`deferredprincipal_daily`](#col-20) | `decimal` | — | Deferred principal from daily snapshot (current month-end). |
| 21 | [`deferredprincipal_diff_remitvsdaily`](#col-21) | `decimal` | — | deferredprincipal_remit − deferredprincipal_daily. Non-zero … |
| 22 | [`deferredint_remit`](#col-22) | `decimal` | — | Deferred interest as reported (portmonth.deferredint). |
| 23 | [`deferredint_daily`](#col-23) | `decimal` | — | Deferred interest from daily snapshot (current month-end). |
| 24 | [`deferredint_diff_remitvsdaily`](#col-24) | `decimal` | — | deferredint_remit − deferredint_daily. Non-zero highlighted. |
| 25 | [`pandi_remit`](#col-25) | `decimal` | — | P&I received per servicer (portmonth.pandireceived). |
| 26 | [`pandiexpected_daily`](#col-26) | `decimal` | — | Scheduled P&I from daily snapshot (basic_data_daily_loan_com… |
| 27 | [`pandi_schedule_diff_remitvsdaily`](#col-27) | `decimal` | — | coalesce(monthly.sched_pandi, portmonth.pandi) − daily.sched… |
| 28 | [`principalreceived_daily`](#col-28) | `decimal` | — | principalpaidmtd from daily snapshot (current month-end). |
| 29 | [`interestreceived_daily`](#col-29) | `decimal` | — | interestpaidmtd from daily snapshot (current month-end). |
| 30 | [`pandireceived_daily`](#col-30) | `decimal` | — | principalpaidmtd + interestpaidmtd from daily snapshot; null… |
| 31 | [`pandi_diff_remitvsdaily`](#col-31) | `decimal` | — | pandireceived(remit) − pandireceived_daily; null when daily … |
| 32 | [`pandi_paid_times_remit`](#col-32) | `float` | — | pandireceived_remit / schedule_pandi_daily; null if schedule… |
| 33 | [`pandi_paid_times_daily`](#col-33) | `float` | — | pandireceived_daily / schedule_pandi_daily; null on missing … |
| 34 | [`delinquency_status_mba`](#col-34) | `string` | — | MBA delinquency status from daily snapshot (delq_status). |
| 35 | [`asofdate`](#col-35) | `date` | — | Remit date (set in Python after SQL). |

## Column logic cards


### <a name="col-1"></a>`loanid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Internal loan id (join key).

**业务规则 (ZH)**: 内部 loan id（关联键）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-2"></a>`mrc_ln`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): MRC servicer loan number (svcloanid from portmonth).

**业务规则 (ZH)**: MRC servicer 贷款号（portmonth.svcloanid）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-3"></a>`dealid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Deal id; portmonth first, falls back to portfunding.

**业务规则 (ZH)**: Deal id；优先 portmonth，缺则 portfunding。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-4"></a>`intrate_remit`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Interest rate as reported by servicer (portmonth.intrate).

**业务规则 (ZH)**: Servicer 上报利率（portmonth.intrate）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-5"></a>`intrate_daily`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Interest rate in daily snapshot (basic_data_daily_loan_common.interest_rate, current month-end).

**业务规则 (ZH)**: Daily 快照利率（basic_data_daily_loan_common.interest_rate，当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-6"></a>`intrate_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): intrate_remit − intrate_daily. Non-zero highlighted.

**业务规则 (ZH)**: intrate_remit − intrate_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-7"></a>`nextduedate_remit`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Next due date as reported (portmonth.nextduedate).

**业务规则 (ZH)**: Servicer 上报下次到期日（portmonth.nextduedate）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-8"></a>`nextduedate_daily`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Next due date in daily snapshot (current month-end).

**业务规则 (ZH)**: Daily 快照中的下次到期日（当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-9"></a>`nextduedate_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): 0 if dates match, 1 if they differ. Non-zero highlighted.

**业务规则 (ZH)**: 日期相同为 0，不同为 1。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-10"></a>`begbal_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Beginning balance as reported (portmonth.prevbal).

**业务规则 (ZH)**: Servicer 上报期初余额（portmonth.prevbal）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-11"></a>`begbal_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Beginning balance from daily snapshot (prior month-end principalbalance).

**业务规则 (ZH)**: Daily 快照期初余额（上月末 principalbalance）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-12"></a>`begbal_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): begbal_remit − begbal_daily. Non-zero highlighted.

**业务规则 (ZH)**: begbal_remit − begbal_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-13"></a>`endbal_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Ending balance as reported (portmonth.balance).

**业务规则 (ZH)**: Servicer 上报期末余额（portmonth.balance）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-14"></a>`endbal_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Ending balance from daily snapshot (current month-end principalbalance).

**业务规则 (ZH)**: Daily 快照期末余额（当月末 principalbalance）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-15"></a>`endbal_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): endbal_remit − endbal_daily. Non-zero highlighted.

**业务规则 (ZH)**: endbal_remit − endbal_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-16"></a>`principal_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Principal received per servicer (portmonth.principalreceived).

**业务规则 (ZH)**: Servicer 上报本金收回（portmonth.principalreceived）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-17"></a>`interest_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Interest received per servicer (portmonth.interestreceived).

**业务规则 (ZH)**: Servicer 上报利息收回（portmonth.interestreceived）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-18"></a>`prin_bal_diff_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): prevbal − balance − principalreceived (should be ~0 for a clean remit).

**业务规则 (ZH)**: prevbal − balance − principalreceived（remit 干净时应 ≈ 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-19"></a>`deferredprincipal_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Deferred principal as reported (portmonth.deferredprin).

**业务规则 (ZH)**: Servicer 上报 deferred principal（portmonth.deferredprin）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-20"></a>`deferredprincipal_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Deferred principal from daily snapshot (current month-end).

**业务规则 (ZH)**: Daily 快照 deferred principal（当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-21"></a>`deferredprincipal_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): deferredprincipal_remit − deferredprincipal_daily. Non-zero highlighted.

**业务规则 (ZH)**: deferredprincipal_remit − deferredprincipal_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-22"></a>`deferredint_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Deferred interest as reported (portmonth.deferredint).

**业务规则 (ZH)**: Servicer 上报 deferred interest（portmonth.deferredint）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-23"></a>`deferredint_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Deferred interest from daily snapshot (current month-end).

**业务规则 (ZH)**: Daily 快照 deferred interest（当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-24"></a>`deferredint_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): deferredint_remit − deferredint_daily. Non-zero highlighted.

**业务规则 (ZH)**: deferredint_remit − deferredint_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-25"></a>`pandi_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): P&I received per servicer (portmonth.pandireceived).

**业务规则 (ZH)**: Servicer 上报 P&I 收回（portmonth.pandireceived）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-26"></a>`pandiexpected_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Scheduled P&I from daily snapshot (basic_data_daily_loan_common.schedule_pandi_daily).

**业务规则 (ZH)**: Daily 快照计划 P&I（basic_data_daily_loan_common.schedule_pandi_daily）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-27"></a>`pandi_schedule_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): coalesce(monthly.sched_pandi, portmonth.pandi) − daily.schedule_pandi_daily. Non-zero highlighted.

**业务规则 (ZH)**: coalesce(monthly.sched_pandi, portmonth.pandi) − daily.schedule_pandi_daily。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-28"></a>`principalreceived_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): principalpaidmtd from daily snapshot (current month-end).

**业务规则 (ZH)**: Daily 快照 principalpaidmtd（当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-29"></a>`interestreceived_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): interestpaidmtd from daily snapshot (current month-end).

**业务规则 (ZH)**: Daily 快照 interestpaidmtd（当月末）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-30"></a>`pandireceived_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): principalpaidmtd + interestpaidmtd from daily snapshot; null if both are null.

**业务规则 (ZH)**: Daily 快照 principalpaidmtd + interestpaidmtd；两者皆空则为空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-31"></a>`pandi_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): pandireceived(remit) − pandireceived_daily; null when daily side is fully null.

**业务规则 (ZH)**: pandireceived(remit) − pandireceived_daily；daily 侧全空时为空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-32"></a>`pandi_paid_times_remit`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): pandireceived_remit / schedule_pandi_daily; null if scheduled is 0.

**业务规则 (ZH)**: pandireceived_remit / schedule_pandi_daily；schedule 为 0 则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-33"></a>`pandi_paid_times_daily`

| Attribute | Value |
|---|---|
| **Type** | `float` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): pandireceived_daily / schedule_pandi_daily; null on missing inputs.

**业务规则 (ZH)**: pandireceived_daily / schedule_pandi_daily；输入缺失则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-34"></a>`delinquency_status_mba`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): MBA delinquency status from daily snapshot (delq_status).

**业务规则 (ZH)**: MBA 拖欠状态，取自 daily 快照（delq_status）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-35"></a>`asofdate`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**Business rule** (EN): Remit date (set in Python after SQL).

**业务规则 (ZH)**: Remit 日期（SQL 后在 Python 中赋值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---

