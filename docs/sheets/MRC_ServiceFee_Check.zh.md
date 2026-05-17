# Sheet —— MRC_ServiceFee_Check

贷款级服务费对账：MRC 贷款级 remit 明细 vs portmonth 合并后的 servicefee。
差额非零即提示聚合不一致。


**产出该 sheet 的 validators**：[`mrc/service_fee_check`](../validators/mrc/service_fee_check.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`fctrdt`](#col-1) | `date` | — | 来自 portmrcremitloanlevelrecap … |
| 2 | [`loanid`](#col-2) | `string` | — | portmrcremitloanlevelrecap 中的内… |
| 3 | [`mrc_ln`](#col-3) | `string` | — | MRC servicer 的贷款号。 |
| 4 | [`dealid`](#col-4) | `string` | — | Deal id，优先取 portmonth；缺则回退到 po… |
| 5 | [`servicefee_remit_raw`](#col-5) | `decimal` | — | portmrcremitloanlevelrecap 的 t… |
| 6 | [`servicefee_portmonth`](#col-6) | `decimal` | — | port.portmonth 的 servicefee（合并… |
| 7 | [`servicefee_diff`](#col-7) | `decimal` | — | servicefee_remit_raw − service… |
| 8 | [`asofdate`](#col-8) | `date` | — | Remit 日期（SQL 后在 Python 中赋值）。 |

## 字段逻辑卡片


### <a name="col-1"></a>`fctrdt`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：来自 portmrcremitloanlevelrecap 的因子日期。

**Business rule (EN)**: Factor date from portmrcremitloanlevelrecap.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-2"></a>`loanid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：portmrcremitloanlevelrecap 中的内部 loan id。

**Business rule (EN)**: Internal loan id from portmrcremitloanlevelrecap.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-3"></a>`mrc_ln`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：MRC servicer 的贷款号。

**Business rule (EN)**: MRC servicer loan number.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-4"></a>`dealid`

| 属性 | 值 |
|---|---|
| **类型** | `string` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：Deal id，优先取 portmonth；缺则回退到 portfunding。

**Business rule (EN)**: Deal id, taken from portmonth first; falls back to portfunding.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-5"></a>`servicefee_remit_raw`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：portmrcremitloanlevelrecap 的 total_accrued_earned_servicing_fees（贷款级原始值）。

**Business rule (EN)**: total_accrued_earned_servicing_fees from portmrcremitloanlevelrecap (loan-level raw).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-6"></a>`servicefee_portmonth`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：port.portmonth 的 servicefee（合并后，MRC）。

**Business rule (EN)**: servicefee from port.portmonth (consolidated, MRC).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-7"></a>`servicefee_diff`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：servicefee_remit_raw − servicefee_portmonth。非零 = 聚合不一致。

**Business rule (EN)**: servicefee_remit_raw − servicefee_portmonth. Non-zero = aggregation mismatch.

!!! info "业务影响"
    非零时报表中高亮显示，运维核查。

*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-8"></a>`asofdate`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/service_fee_check`](../validators/mrc/service_fee_check.md) |

**业务规则（中文）**：Remit 日期（SQL 后在 Python 中赋值）。

**Business rule (EN)**: Remit date (set in Python after SQL).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---

