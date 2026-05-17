# Sheet — MRC_Advance_Check

Loan-level advance-balance reconciliation for MRC. For each loan, escrow / recoverable
corp / non-recoverable corp advance balances are compared between remit (portmonth _chg
fields) and daily snapshot (curr - prev month-end). Non-zero "_diff_remitvsdaily" =
potential servicer reporting issue.


**Producing validators**: [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md)
## Columns

Click any column to expand its full logic card.

| # | Column | Type | Sources | Rule (short) |
|---|---|---|---|---|
| 1 | [`loanid`](#col-1) | `string` | — | Internal loan id (join key). |
| 2 | [`mrc_ln`](#col-2) | `string` | — | MRC servicer loan number (portmonth.svcloanid). |
| 3 | [`dealid`](#col-3) | `string` | — | Deal id; portmonth first, falls back to portfunding. |
| 4 | [`delq_status`](#col-4) | `string` | — | Delinquency status from prior month-end daily snapshot. |
| 5 | [`escrowadv_prev_daily`](#col-5) | `decimal` | — | Escrow advance balance at prior month-end (coalesce to 0). |
| 6 | [`escrowadv_curr_daily`](#col-6) | `decimal` | — | Escrow advance balance at current month-end (coalesce to 0). |
| 7 | [`escrowadv_chg_daily`](#col-7) | `decimal` | — | escrowadv_curr_daily − escrowadv_prev_daily; null if either … |
| 8 | [`escadv_remit`](#col-8) | `decimal` | — | Servicer-reported escrow advance change (portmonth.escrowadv… |
| 9 | [`escadv_diff_remitvsdaily`](#col-9) | `decimal` | — | escrowadv_chg_daily + escadv_remit. Non-zero highlighted (si… |
| 10 | [`reccorpadvance_prev_daily`](#col-10) | `decimal` | — | Recoverable corp advance balance at prior month-end (coalesc… |
| 11 | [`reccorpadvance_curr_daily`](#col-11) | `decimal` | — | Recoverable corp advance balance at current month-end (coale… |
| 12 | [`reccorpadvance_chg_daily`](#col-12) | `decimal` | — | curr − prev daily; null if either daily side is missing. |
| 13 | [`reccorpadvance_remit`](#col-13) | `decimal` | — | Servicer-reported recoverable corp advance change (portmonth… |
| 14 | [`recovcorpadv_diff_remitvsdaily`](#col-14) | `decimal` | — | reccorpadvance_chg_daily + reccorpadvance_remit. Non-zero hi… |
| 15 | [`nonrecovcorpadv_prev_daily`](#col-15) | `decimal` | — | Non-recoverable corp advance balance at prior month-end (coa… |
| 16 | [`nonrecovcorpadv_curr_daily`](#col-16) | `decimal` | — | Non-recoverable corp advance balance at current month-end (c… |
| 17 | [`nonrecovcorpadv_chg_daily`](#col-17) | `decimal` | — | curr − prev daily; null if either daily side is missing. |
| 18 | [`nonrecovadvance_remit`](#col-18) | `decimal` | — | Servicer-reported non-recoverable corp advance change (portm… |
| 19 | [`nonrecovcorpadv_diff_remitvsdaily`](#col-19) | `decimal` | — | nonrecovcorpadv_chg_daily + nonrecovadvance_remit. Non-zero … |
| 20 | [`totalcorpadv_prev_daily`](#col-20) | `decimal` | — | reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily. |
| 21 | [`totalcorpadv_curr_daily`](#col-21) | `decimal` | — | reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily. |
| 22 | [`totalcorpadv_chg_daily`](#col-22) | `decimal` | — | totalcorpadv_curr_daily − totalcorpadv_prev_daily; null if e… |
| 23 | [`totalcorpadvance_remit`](#col-23) | `decimal` | — | Servicer-reported total corp adv change: coalesce(portmonth.… |
| 24 | [`totalcorpadv_diff_remitvsdaily`](#col-24) | `decimal` | — | totalcorpadv_chg_daily + totalcorpadvance_remit. Non-zero hi… |
| 25 | [`escrow_balance_prev`](#col-25) | `decimal` | — | Escrow balance at prior month-end (basic_data_daily_loan_com… |
| 26 | [`escrow_balance_curr`](#col-26) | `decimal` | — | Escrow balance at current month-end (basic_data_daily_loan_c… |
| 27 | [`asofdate`](#col-27) | `date` | — | Remit date (set in Python after SQL). |

## Column logic cards


### <a name="col-1"></a>`loanid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Internal loan id (join key).

**业务规则 (ZH)**: 内部 loan id（关联键）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-2"></a>`mrc_ln`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): MRC servicer loan number (portmonth.svcloanid).

**业务规则 (ZH)**: MRC servicer 贷款号（portmonth.svcloanid）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-3"></a>`dealid`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Deal id; portmonth first, falls back to portfunding.

**业务规则 (ZH)**: Deal id；优先 portmonth，缺则 portfunding。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-4"></a>`delq_status`

| Attribute | Value |
|---|---|
| **Type** | `string` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Delinquency status from prior month-end daily snapshot.

**业务规则 (ZH)**: 拖欠状态，取自上月末 daily 快照。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-5"></a>`escrowadv_prev_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Escrow advance balance at prior month-end (coalesce to 0).

**业务规则 (ZH)**: 上月末 escrow advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-6"></a>`escrowadv_curr_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Escrow advance balance at current month-end (coalesce to 0).

**业务规则 (ZH)**: 当月末 escrow advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-7"></a>`escrowadv_chg_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): escrowadv_curr_daily − escrowadv_prev_daily; null if either daily side is missing.

**业务规则 (ZH)**: escrowadv_curr_daily − escrowadv_prev_daily；任一 daily 侧缺则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-8"></a>`escadv_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Servicer-reported escrow advance change (portmonth.escrowadv_chg, coalesce to 0).

**业务规则 (ZH)**: Servicer 上报 escrow advance 变动（portmonth.escrowadv_chg，缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-9"></a>`escadv_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): escrowadv_chg_daily + escadv_remit. Non-zero highlighted (sign convention: remit reports change as outflow).

**业务规则 (ZH)**: escrowadv_chg_daily + escadv_remit。非零高亮（符号约定：remit 把变动当流出）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-10"></a>`reccorpadvance_prev_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Recoverable corp advance balance at prior month-end (coalesce to 0).

**业务规则 (ZH)**: 上月末可回收 corp advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-11"></a>`reccorpadvance_curr_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Recoverable corp advance balance at current month-end (coalesce to 0).

**业务规则 (ZH)**: 当月末可回收 corp advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-12"></a>`reccorpadvance_chg_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): curr − prev daily; null if either daily side is missing.

**业务规则 (ZH)**: curr − prev daily；任一 daily 侧缺则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-13"></a>`reccorpadvance_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Servicer-reported recoverable corp advance change (portmonth.corpadvrec_chg, coalesce 0).

**业务规则 (ZH)**: Servicer 上报可回收 corp advance 变动（portmonth.corpadvrec_chg，缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-14"></a>`recovcorpadv_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): reccorpadvance_chg_daily + reccorpadvance_remit. Non-zero highlighted.

**业务规则 (ZH)**: reccorpadvance_chg_daily + reccorpadvance_remit。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-15"></a>`nonrecovcorpadv_prev_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Non-recoverable corp advance balance at prior month-end (coalesce to 0).

**业务规则 (ZH)**: 上月末不可回收 corp advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-16"></a>`nonrecovcorpadv_curr_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Non-recoverable corp advance balance at current month-end (coalesce to 0).

**业务规则 (ZH)**: 当月末不可回收 corp advance 余额（缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-17"></a>`nonrecovcorpadv_chg_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): curr − prev daily; null if either daily side is missing.

**业务规则 (ZH)**: curr − prev daily；任一 daily 侧缺则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-18"></a>`nonrecovadvance_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Servicer-reported non-recoverable corp advance change (portmonth.corpadvnonrec_chg, coalesce 0).

**业务规则 (ZH)**: Servicer 上报不可回收 corp advance 变动（portmonth.corpadvnonrec_chg，缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-19"></a>`nonrecovcorpadv_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): nonrecovcorpadv_chg_daily + nonrecovadvance_remit. Non-zero highlighted.

**业务规则 (ZH)**: nonrecovcorpadv_chg_daily + nonrecovadvance_remit。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-20"></a>`totalcorpadv_prev_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily.

**业务规则 (ZH)**: reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-21"></a>`totalcorpadv_curr_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily.

**业务规则 (ZH)**: reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-22"></a>`totalcorpadv_chg_daily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): totalcorpadv_curr_daily − totalcorpadv_prev_daily; null if either daily side missing.

**业务规则 (ZH)**: totalcorpadv_curr_daily − totalcorpadv_prev_daily；任一 daily 侧缺则空。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-23"></a>`totalcorpadvance_remit`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Servicer-reported total corp adv change: coalesce(portmonth.corpadvtotal_chg, corpadvrec_chg + corpadvnonrec_chg).

**业务规则 (ZH)**: Servicer 上报 corp adv 总变动：coalesce(portmonth.corpadvtotal_chg, corpadvrec_chg + corpadvnonrec_chg)。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-24"></a>`totalcorpadv_diff_remitvsdaily`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): totalcorpadv_chg_daily + totalcorpadvance_remit. Non-zero highlighted.

**业务规则 (ZH)**: totalcorpadv_chg_daily + totalcorpadvance_remit。非零高亮。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-25"></a>`escrow_balance_prev`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Escrow balance at prior month-end (basic_data_daily_loan_common.escrowbalance, coalesce 0).

**业务规则 (ZH)**: 上月末 escrow 余额（basic_data_daily_loan_common.escrowbalance，缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-26"></a>`escrow_balance_curr`

| Attribute | Value |
|---|---|
| **Type** | `decimal` |
| **Format** | `currency` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Escrow balance at current month-end (basic_data_daily_loan_common.escrowbalance, coalesce 0).

**业务规则 (ZH)**: 当月末 escrow 余额（basic_data_daily_loan_common.escrowbalance，缺则 0）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---


### <a name="col-27"></a>`asofdate`

| Attribute | Value |
|---|---|
| **Type** | `date` |
| **Related validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**Business rule** (EN): Remit date (set in Python after SQL).

**业务规则 (ZH)**: Remit 日期（SQL 后在 Python 中赋值）。


*(No source lineage extracted yet — sqlglot may have failed or this is a Python-only column.)*



---

