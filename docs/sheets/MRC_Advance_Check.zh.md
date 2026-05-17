# Sheet —— MRC_Advance_Check

MRC 贷款级 advance 余额对账。每笔贷款：escrow / 可回收 corp / 不可回收 corp advance
在 remit（portmonth _chg 字段）与 daily 快照（当月末 - 上月末）之间比对。
"_diff_remitvsdaily" 非零 = servicer 上报可能有问题。


**产出该 sheet 的 validators**：[`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`loanid`](#col-1) | `string` | — | 内部 loan id（关联键）。 |
| 2 | [`mrc_ln`](#col-2) | `string` | — | MRC servicer 贷款号（portmonth.svc… |
| 3 | [`dealid`](#col-3) | `string` | — | Deal id；优先 portmonth，缺则 portfu… |
| 4 | [`delq_status`](#col-4) | `string` | — | 拖欠状态，取自上月末 daily 快照。 |
| 5 | [`escrowadv_prev_daily`](#col-5) | `decimal` | — | 上月末 escrow advance 余额（缺则 0）。 |
| 6 | [`escrowadv_curr_daily`](#col-6) | `decimal` | — | 当月末 escrow advance 余额（缺则 0）。 |
| 7 | [`escrowadv_chg_daily`](#col-7) | `decimal` | — | escrowadv_curr_daily − escrowa… |
| 8 | [`escadv_remit`](#col-8) | `decimal` | — | Servicer 上报 escrow advance 变动（… |
| 9 | [`escadv_diff_remitvsdaily`](#col-9) | `decimal` | — | escrowadv_chg_daily + escadv_r… |
| 10 | [`reccorpadvance_prev_daily`](#col-10) | `decimal` | — | 上月末可回收 corp advance 余额（缺则 0）。 |
| 11 | [`reccorpadvance_curr_daily`](#col-11) | `decimal` | — | 当月末可回收 corp advance 余额（缺则 0）。 |
| 12 | [`reccorpadvance_chg_daily`](#col-12) | `decimal` | — | curr − prev daily；任一 daily 侧缺则… |
| 13 | [`reccorpadvance_remit`](#col-13) | `decimal` | — | Servicer 上报可回收 corp advance 变动… |
| 14 | [`recovcorpadv_diff_remitvsdaily`](#col-14) | `decimal` | — | reccorpadvance_chg_daily + rec… |
| 15 | [`nonrecovcorpadv_prev_daily`](#col-15) | `decimal` | — | 上月末不可回收 corp advance 余额（缺则 0）。 |
| 16 | [`nonrecovcorpadv_curr_daily`](#col-16) | `decimal` | — | 当月末不可回收 corp advance 余额（缺则 0）。 |
| 17 | [`nonrecovcorpadv_chg_daily`](#col-17) | `decimal` | — | curr − prev daily；任一 daily 侧缺则… |
| 18 | [`nonrecovadvance_remit`](#col-18) | `decimal` | — | Servicer 上报不可回收 corp advance 变… |
| 19 | [`nonrecovcorpadv_diff_remitvsdaily`](#col-19) | `decimal` | — | nonrecovcorpadv_chg_daily + no… |
| 20 | [`totalcorpadv_prev_daily`](#col-20) | `decimal` | — | reccorpadvance_prev_daily + no… |
| 21 | [`totalcorpadv_curr_daily`](#col-21) | `decimal` | — | reccorpadvance_curr_daily + no… |
| 22 | [`totalcorpadv_chg_daily`](#col-22) | `decimal` | — | totalcorpadv_curr_daily − tota… |
| 23 | [`totalcorpadvance_remit`](#col-23) | `decimal` | — | Servicer 上报 corp adv 总变动：coale… |
| 24 | [`totalcorpadv_diff_remitvsdaily`](#col-24) | `decimal` | — | totalcorpadv_chg_daily + total… |
| 25 | [`escrow_balance_prev`](#col-25) | `decimal` | — | 上月末 escrow 余额（basic_data_daily… |
| 26 | [`escrow_balance_curr`](#col-26) | `decimal` | — | 当月末 escrow 余额（basic_data_daily… |
| 27 | [`asofdate`](#col-27) | `date` | — | Remit 日期（SQL 后在 Python 中赋值）。 |

## 字段逻辑卡片


### <a name="col-1"></a>`loanid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：内部 loan id（关联键）。

**Business rule (EN)**: Internal loan id (join key).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-2"></a>`mrc_ln`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：MRC servicer 贷款号（portmonth.svcloanid）。

**Business rule (EN)**: MRC servicer loan number (portmonth.svcloanid).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-3"></a>`dealid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Deal id；优先 portmonth，缺则 portfunding。

**Business rule (EN)**: Deal id; portmonth first, falls back to portfunding.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-4"></a>`delq_status`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：拖欠状态，取自上月末 daily 快照。

**Business rule (EN)**: Delinquency status from prior month-end daily snapshot.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-5"></a>`escrowadv_prev_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：上月末 escrow advance 余额（缺则 0）。

**Business rule (EN)**: Escrow advance balance at prior month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-6"></a>`escrowadv_curr_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：当月末 escrow advance 余额（缺则 0）。

**Business rule (EN)**: Escrow advance balance at current month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-7"></a>`escrowadv_chg_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：escrowadv_curr_daily − escrowadv_prev_daily；任一 daily 侧缺则空。

**Business rule (EN)**: escrowadv_curr_daily − escrowadv_prev_daily; null if either daily side is missing.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-8"></a>`escadv_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Servicer 上报 escrow advance 变动（portmonth.escrowadv_chg，缺则 0）。

**Business rule (EN)**: Servicer-reported escrow advance change (portmonth.escrowadv_chg, coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-9"></a>`escadv_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：escrowadv_chg_daily + escadv_remit。非零高亮（符号约定：remit 把变动当流出）。

**Business rule (EN)**: escrowadv_chg_daily + escadv_remit. Non-zero highlighted (sign convention: remit reports change as outflow).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-10"></a>`reccorpadvance_prev_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：上月末可回收 corp advance 余额（缺则 0）。

**Business rule (EN)**: Recoverable corp advance balance at prior month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-11"></a>`reccorpadvance_curr_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：当月末可回收 corp advance 余额（缺则 0）。

**Business rule (EN)**: Recoverable corp advance balance at current month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-12"></a>`reccorpadvance_chg_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：curr − prev daily；任一 daily 侧缺则空。

**Business rule (EN)**: curr − prev daily; null if either daily side is missing.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-13"></a>`reccorpadvance_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Servicer 上报可回收 corp advance 变动（portmonth.corpadvrec_chg，缺则 0）。

**Business rule (EN)**: Servicer-reported recoverable corp advance change (portmonth.corpadvrec_chg, coalesce 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-14"></a>`recovcorpadv_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：reccorpadvance_chg_daily + reccorpadvance_remit。非零高亮。

**Business rule (EN)**: reccorpadvance_chg_daily + reccorpadvance_remit. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-15"></a>`nonrecovcorpadv_prev_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：上月末不可回收 corp advance 余额（缺则 0）。

**Business rule (EN)**: Non-recoverable corp advance balance at prior month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-16"></a>`nonrecovcorpadv_curr_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：当月末不可回收 corp advance 余额（缺则 0）。

**Business rule (EN)**: Non-recoverable corp advance balance at current month-end (coalesce to 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-17"></a>`nonrecovcorpadv_chg_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：curr − prev daily；任一 daily 侧缺则空。

**Business rule (EN)**: curr − prev daily; null if either daily side is missing.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-18"></a>`nonrecovadvance_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Servicer 上报不可回收 corp advance 变动（portmonth.corpadvnonrec_chg，缺则 0）。

**Business rule (EN)**: Servicer-reported non-recoverable corp advance change (portmonth.corpadvnonrec_chg, coalesce 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-19"></a>`nonrecovcorpadv_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：nonrecovcorpadv_chg_daily + nonrecovadvance_remit。非零高亮。

**Business rule (EN)**: nonrecovcorpadv_chg_daily + nonrecovadvance_remit. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-20"></a>`totalcorpadv_prev_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily。

**Business rule (EN)**: reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-21"></a>`totalcorpadv_curr_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily。

**Business rule (EN)**: reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-22"></a>`totalcorpadv_chg_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：totalcorpadv_curr_daily − totalcorpadv_prev_daily；任一 daily 侧缺则空。

**Business rule (EN)**: totalcorpadv_curr_daily − totalcorpadv_prev_daily; null if either daily side missing.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-23"></a>`totalcorpadvance_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Servicer 上报 corp adv 总变动：coalesce(portmonth.corpadvtotal_chg, corpadvrec_chg + corpadvnonrec_chg)。

**Business rule (EN)**: Servicer-reported total corp adv change: coalesce(portmonth.corpadvtotal_chg, corpadvrec_chg + corpadvnonrec_chg).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-24"></a>`totalcorpadv_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：totalcorpadv_chg_daily + totalcorpadvance_remit。非零高亮。

**Business rule (EN)**: totalcorpadv_chg_daily + totalcorpadvance_remit. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-25"></a>`escrow_balance_prev`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：上月末 escrow 余额（basic_data_daily_loan_common.escrowbalance，缺则 0）。

**Business rule (EN)**: Escrow balance at prior month-end (basic_data_daily_loan_common.escrowbalance, coalesce 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-26"></a>`escrow_balance_curr`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：当月末 escrow 余额（basic_data_daily_loan_common.escrowbalance，缺则 0）。

**Business rule (EN)**: Escrow balance at current month-end (basic_data_daily_loan_common.escrowbalance, coalesce 0).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-27"></a>`asofdate`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/check_adv_balance`](../validators/mrc/check_adv_balance.md) |

**业务规则（中文）**：Remit 日期（SQL 后在 Python 中赋值）。

**Business rule (EN)**: Remit date (set in Python after SQL).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---

