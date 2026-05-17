# Sheet —— MRC_General_Check

贷款级关键属性对账：servicer remit 报表（port.portmonth）vs 内部 daily 快照
（basic_data_daily_loan_common）。"_remit" 与 "_daily" 配对加 "_diff_remitvsdaily"
差异，标记 servicer 上报可能的错误。


**产出该 sheet 的 validators**：[`mrc/check_general_info`](../validators/mrc/check_general_info.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`loanid`](#col-1) | `string` | — | 内部 loan id（关联键）。 |
| 2 | [`mrc_ln`](#col-2) | `string` | — | MRC servicer 贷款号（portmonth.svc… |
| 3 | [`dealid`](#col-3) | `string` | — | Deal id；优先 portmonth，缺则 portfu… |
| 4 | [`intrate_remit`](#col-4) | `float` | — | Servicer 上报利率（portmonth.intrat… |
| 5 | [`intrate_daily`](#col-5) | `float` | — | Daily 快照利率（basic_data_daily_lo… |
| 6 | [`intrate_diff_remitvsdaily`](#col-6) | `float` | — | intrate_remit − intrate_daily。… |
| 7 | [`nextduedate_remit`](#col-7) | `date` | — | Servicer 上报下次到期日（portmonth.nex… |
| 8 | [`nextduedate_daily`](#col-8) | `date` | — | Daily 快照中的下次到期日（当月末）。 |
| 9 | [`nextduedate_diff_remitvsdaily`](#col-9) | `float` | — | 日期相同为 0，不同为 1。非零高亮。 |
| 10 | [`begbal_remit`](#col-10) | `decimal` | — | Servicer 上报期初余额（portmonth.prev… |
| 11 | [`begbal_daily`](#col-11) | `decimal` | — | Daily 快照期初余额（上月末 principalbala… |
| 12 | [`begbal_diff_remitvsdaily`](#col-12) | `decimal` | — | begbal_remit − begbal_daily。非零… |
| 13 | [`endbal_remit`](#col-13) | `decimal` | — | Servicer 上报期末余额（portmonth.bala… |
| 14 | [`endbal_daily`](#col-14) | `decimal` | — | Daily 快照期末余额（当月末 principalbala… |
| 15 | [`endbal_diff_remitvsdaily`](#col-15) | `decimal` | — | endbal_remit − endbal_daily。非零… |
| 16 | [`principal_remit`](#col-16) | `decimal` | — | Servicer 上报本金收回（portmonth.prin… |
| 17 | [`interest_remit`](#col-17) | `decimal` | — | Servicer 上报利息收回（portmonth.inte… |
| 18 | [`prin_bal_diff_remit`](#col-18) | `decimal` | — | prevbal − balance − principalr… |
| 19 | [`deferredprincipal_remit`](#col-19) | `decimal` | — | Servicer 上报 deferred principal… |
| 20 | [`deferredprincipal_daily`](#col-20) | `decimal` | — | Daily 快照 deferred principal（当月… |
| 21 | [`deferredprincipal_diff_remitvsdaily`](#col-21) | `decimal` | — | deferredprincipal_remit − defe… |
| 22 | [`deferredint_remit`](#col-22) | `decimal` | — | Servicer 上报 deferred interest（… |
| 23 | [`deferredint_daily`](#col-23) | `decimal` | — | Daily 快照 deferred interest（当月末… |
| 24 | [`deferredint_diff_remitvsdaily`](#col-24) | `decimal` | — | deferredint_remit − deferredin… |
| 25 | [`pandi_remit`](#col-25) | `decimal` | — | Servicer 上报 P&I 收回（portmonth.p… |
| 26 | [`pandiexpected_daily`](#col-26) | `decimal` | — | Daily 快照计划 P&I（basic_data_dail… |
| 27 | [`pandi_schedule_diff_remitvsdaily`](#col-27) | `decimal` | — | coalesce(monthly.sched_pandi, … |
| 28 | [`principalreceived_daily`](#col-28) | `decimal` | — | Daily 快照 principalpaidmtd（当月末）… |
| 29 | [`interestreceived_daily`](#col-29) | `decimal` | — | Daily 快照 interestpaidmtd（当月末）。 |
| 30 | [`pandireceived_daily`](#col-30) | `decimal` | — | Daily 快照 principalpaidmtd + in… |
| 31 | [`pandi_diff_remitvsdaily`](#col-31) | `decimal` | — | pandireceived(remit) − pandire… |
| 32 | [`pandi_paid_times_remit`](#col-32) | `float` | — | pandireceived_remit / schedule… |
| 33 | [`pandi_paid_times_daily`](#col-33) | `float` | — | pandireceived_daily / schedule… |
| 34 | [`delinquency_status_mba`](#col-34) | `string` | — | MBA 拖欠状态，取自 daily 快照（delq_stat… |
| 35 | [`asofdate`](#col-35) | `date` | — | Remit 日期（SQL 后在 Python 中赋值）。 |

## 字段逻辑卡片


### <a name="col-1"></a>`loanid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：内部 loan id（关联键）。

**Business rule (EN)**: Internal loan id (join key).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-2"></a>`mrc_ln`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：MRC servicer 贷款号（portmonth.svcloanid）。

**Business rule (EN)**: MRC servicer loan number (svcloanid from portmonth).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-3"></a>`dealid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Deal id；优先 portmonth，缺则 portfunding。

**Business rule (EN)**: Deal id; portmonth first, falls back to portfunding.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-4"></a>`intrate_remit`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报利率（portmonth.intrate）。

**Business rule (EN)**: Interest rate as reported by servicer (portmonth.intrate).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-5"></a>`intrate_daily`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照利率（basic_data_daily_loan_common.interest_rate，当月末）。

**Business rule (EN)**: Interest rate in daily snapshot (basic_data_daily_loan_common.interest_rate, current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-6"></a>`intrate_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：intrate_remit − intrate_daily。非零高亮。

**Business rule (EN)**: intrate_remit − intrate_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-7"></a>`nextduedate_remit`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报下次到期日（portmonth.nextduedate）。

**Business rule (EN)**: Next due date as reported (portmonth.nextduedate).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-8"></a>`nextduedate_daily`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照中的下次到期日（当月末）。

**Business rule (EN)**: Next due date in daily snapshot (current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-9"></a>`nextduedate_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：日期相同为 0，不同为 1。非零高亮。

**Business rule (EN)**: 0 if dates match, 1 if they differ. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-10"></a>`begbal_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报期初余额（portmonth.prevbal）。

**Business rule (EN)**: Beginning balance as reported (portmonth.prevbal).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-11"></a>`begbal_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照期初余额（上月末 principalbalance）。

**Business rule (EN)**: Beginning balance from daily snapshot (prior month-end principalbalance).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-12"></a>`begbal_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：begbal_remit − begbal_daily。非零高亮。

**Business rule (EN)**: begbal_remit − begbal_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-13"></a>`endbal_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报期末余额（portmonth.balance）。

**Business rule (EN)**: Ending balance as reported (portmonth.balance).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-14"></a>`endbal_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照期末余额（当月末 principalbalance）。

**Business rule (EN)**: Ending balance from daily snapshot (current month-end principalbalance).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-15"></a>`endbal_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：endbal_remit − endbal_daily。非零高亮。

**Business rule (EN)**: endbal_remit − endbal_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-16"></a>`principal_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报本金收回（portmonth.principalreceived）。

**Business rule (EN)**: Principal received per servicer (portmonth.principalreceived).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-17"></a>`interest_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报利息收回（portmonth.interestreceived）。

**Business rule (EN)**: Interest received per servicer (portmonth.interestreceived).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-18"></a>`prin_bal_diff_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：prevbal − balance − principalreceived（remit 干净时应 ≈ 0）。

**Business rule (EN)**: prevbal − balance − principalreceived (should be ~0 for a clean remit).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-19"></a>`deferredprincipal_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报 deferred principal（portmonth.deferredprin）。

**Business rule (EN)**: Deferred principal as reported (portmonth.deferredprin).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-20"></a>`deferredprincipal_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照 deferred principal（当月末）。

**Business rule (EN)**: Deferred principal from daily snapshot (current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-21"></a>`deferredprincipal_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：deferredprincipal_remit − deferredprincipal_daily。非零高亮。

**Business rule (EN)**: deferredprincipal_remit − deferredprincipal_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-22"></a>`deferredint_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报 deferred interest（portmonth.deferredint）。

**Business rule (EN)**: Deferred interest as reported (portmonth.deferredint).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-23"></a>`deferredint_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照 deferred interest（当月末）。

**Business rule (EN)**: Deferred interest from daily snapshot (current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-24"></a>`deferredint_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：deferredint_remit − deferredint_daily。非零高亮。

**Business rule (EN)**: deferredint_remit − deferredint_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-25"></a>`pandi_remit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Servicer 上报 P&I 收回（portmonth.pandireceived）。

**Business rule (EN)**: P&I received per servicer (portmonth.pandireceived).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-26"></a>`pandiexpected_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照计划 P&I（basic_data_daily_loan_common.schedule_pandi_daily）。

**Business rule (EN)**: Scheduled P&I from daily snapshot (basic_data_daily_loan_common.schedule_pandi_daily).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-27"></a>`pandi_schedule_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：coalesce(monthly.sched_pandi, portmonth.pandi) − daily.schedule_pandi_daily。非零高亮。

**Business rule (EN)**: coalesce(monthly.sched_pandi, portmonth.pandi) − daily.schedule_pandi_daily. Non-zero highlighted.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-28"></a>`principalreceived_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照 principalpaidmtd（当月末）。

**Business rule (EN)**: principalpaidmtd from daily snapshot (current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-29"></a>`interestreceived_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照 interestpaidmtd（当月末）。

**Business rule (EN)**: interestpaidmtd from daily snapshot (current month-end).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-30"></a>`pandireceived_daily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Daily 快照 principalpaidmtd + interestpaidmtd；两者皆空则为空。

**Business rule (EN)**: principalpaidmtd + interestpaidmtd from daily snapshot; null if both are null.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-31"></a>`pandi_diff_remitvsdaily`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：pandireceived(remit) − pandireceived_daily；daily 侧全空时为空。

**Business rule (EN)**: pandireceived(remit) − pandireceived_daily; null when daily side is fully null.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-32"></a>`pandi_paid_times_remit`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：pandireceived_remit / schedule_pandi_daily；schedule 为 0 则空。

**Business rule (EN)**: pandireceived_remit / schedule_pandi_daily; null if scheduled is 0.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-33"></a>`pandi_paid_times_daily`

| 属性 | 值 |
|---|---|
| **类型** | `float` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：pandireceived_daily / schedule_pandi_daily；输入缺失则空。

**Business rule (EN)**: pandireceived_daily / schedule_pandi_daily; null on missing inputs.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-34"></a>`delinquency_status_mba`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：MBA 拖欠状态，取自 daily 快照（delq_status）。

**Business rule (EN)**: MBA delinquency status from daily snapshot (delq_status).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-35"></a>`asofdate`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/check_general_info`](../validators/mrc/check_general_info.md) |

**业务规则（中文）**：Remit 日期（SQL 后在 Python 中赋值）。

**Business rule (EN)**: Remit date (set in Python after SQL).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---

