# Sheet —— MRC_Summary_check

对当月所有 MRC 贷款的 remit 关键金额做单行聚合，用于核对 servicer 上报总量是否合理。


**产出该 sheet 的 validators**：[`mrc/summary_check`](../validators/mrc/summary_check.md)
## 字段列表

点击任一字段查看完整逻辑卡片。

| # | 字段 | 类型 | 来源 | 规则（简） |
|---|---|---|---|---|
| 1 | [`principalreceived`](#col-1) | `decimal` | — | 当期 fctrdt 所有 MRC 贷款 principalr… |
| 2 | [`interestreceived`](#col-2) | `decimal` | — | 当期 fctrdt 所有 MRC 贷款 interestre… |
| 3 | [`escrowadv_chg`](#col-3) | `decimal` | — | 所有 MRC 贷款 escrowadv_chg（escrow… |
| 4 | [`corpadvrec_chg`](#col-4) | `decimal` | — | 可回收 corp advance 变动（corpadvrec… |
| 5 | [`corpadvnonrec_chg`](#col-5) | `decimal` | — | 不可回收 corp advance 变动（corpadvno… |
| 6 | [`corpadvtotal_chg`](#col-6) | `decimal` | — | 全部 corp advance 变动（可回收 + 不可回收）… |
| 7 | [`servicefee`](#col-7) | `decimal` | — | 所有 MRC 贷款基础服务费的总和。 |
| 8 | [`otherfees`](#col-8) | `decimal` | — | 所有 MRC 贷款其他费用的总和。 |
| 9 | [`totalservicefee`](#col-9) | `decimal` | — | 所有 MRC 贷款 servicefee + otherfe… |
| 10 | [`subremit`](#col-10) | `decimal` | — | 所有 MRC 贷款 subremit 的总和。 |
| 11 | [`totremit`](#col-11) | `decimal` | — | 所有 MRC 贷款 totremit 的总和。 |
| 12 | [`beginningbalance`](#col-12) | `decimal` | — | 所有 MRC 贷款 prevbal（期初余额）的总和。 |
| 13 | [`endingbalance`](#col-13) | `decimal` | — | 所有 MRC 贷款 balance（期末余额）的总和。 |
| 14 | [`asofdate`](#col-14) | `date` | — | Remit 日期（聚合后在 Python 中赋值）。 |

## 字段逻辑卡片


### <a name="col-1"></a>`principalreceived`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：当期 fctrdt 所有 MRC 贷款 principalreceived 的总和。

**Business rule (EN)**: Sum of principalreceived across all MRC loans for the current fctrdt.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-2"></a>`interestreceived`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：当期 fctrdt 所有 MRC 贷款 interestreceived 的总和。

**Business rule (EN)**: Sum of interestreceived across all MRC loans for the current fctrdt.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-3"></a>`escrowadv_chg`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 escrowadv_chg（escrow advance 变动）的总和。

**Business rule (EN)**: Sum of escrowadv_chg (escrow advance change) across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-4"></a>`corpadvrec_chg`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：可回收 corp advance 变动（corpadvrec_chg）的总和。

**Business rule (EN)**: Sum of recoverable corp advance change (corpadvrec_chg).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-5"></a>`corpadvnonrec_chg`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：不可回收 corp advance 变动（corpadvnonrec_chg）的总和。

**Business rule (EN)**: Sum of non-recoverable corp advance change (corpadvnonrec_chg).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-6"></a>`corpadvtotal_chg`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：全部 corp advance 变动（可回收 + 不可回收）的总和。

**Business rule (EN)**: Sum of total corp advance change (recoverable + non-recoverable).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-7"></a>`servicefee`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款基础服务费的总和。

**Business rule (EN)**: Sum of base service fee across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-8"></a>`otherfees`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款其他费用的总和。

**Business rule (EN)**: Sum of other fees across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-9"></a>`totalservicefee`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 servicefee + otherfees 的总和。

**Business rule (EN)**: Sum of servicefee + otherfees across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-10"></a>`subremit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 subremit 的总和。

**Business rule (EN)**: Sum of subremit across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-11"></a>`totremit`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 totremit 的总和。

**Business rule (EN)**: Sum of totremit across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-12"></a>`beginningbalance`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 prevbal（期初余额）的总和。

**Business rule (EN)**: Sum of prevbal (beginning balance) across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-13"></a>`endingbalance`

| 属性 | 值 |
|---|---|
| **类型** | `decimal` |
| **格式** | `currency` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：所有 MRC 贷款 balance（期末余额）的总和。

**Business rule (EN)**: Sum of balance (ending balance) across all MRC loans.


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---


### <a name="col-14"></a>`asofdate`

| 属性 | 值 |
|---|---|
| **类型** | `date` |
| **关联 validator** | [`mrc/summary_check`](../validators/mrc/summary_check.md) |

**业务规则（中文）**：Remit 日期（聚合后在 Python 中赋值）。

**Business rule (EN)**: Remit date (set in Python after aggregation).


*（尚未抽取到列级来源——可能 sqlglot 解析失败，或这是纯 Python 列。）*



---

