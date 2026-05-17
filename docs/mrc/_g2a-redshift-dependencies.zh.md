# _G2a A6 — Redshift 依赖目录

<!-- G2A-A6: OPERATOR-ONLY — 此文件枚举执行 G2a 快照导出所需的全部 Redshift 访问前提。Agent 无法独立满足这些依赖；必须由拥有 VPN + Vault token 的人类操作员执行。 -->
<!-- LIVING-DOC: 当连接参数、凭证路径或 SQL 表名变化时必须更新本文。 -->

> **文档定位 / Purpose**：G2a 快照导出（`tools/freeze_snapshot.py export`）是
> **operator-only** 操作——需要 Redshift VPN 访问权限与 HashiCorp Vault token。
> 本文是一站式依赖清单，让任何操作员（当前用户、同事、未来 Copilot session）都能
> 在不翻阅源码的情况下知道：需要什么 Redshift 访问才能跑通 G2a。
>
> **目标读者 / Audience**：有 Redshift 访问权限的操作员；接手 G2a 的下一位 agent。
>
> **修订历史 / Revision history**
>
> | 日期 | 作者 | 变更 |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — G2a A6 首版。源自 `cred/__init__.py`、`cred/db_cred.py`、`config/db_conn.py`、`flow/__init__.py`、`_export_queries/_coverage.md`、`docs/mrc/1.1-rawdata.zh.md`。 |

---

## 1. 本文存在的理由

G2a（`mrc-snapshot` todo）的目标是把 MRC 5 个 validator 实际读取的 Redshift
数据集导出到 `baselines/mrc/2026-04-30/input_snapshots/parquet/` 下的 Parquet
文件，以便 Stage 2 的 Parquet-reading shim 在**零 Redshift 依赖**的情况下重跑
验证报告。

**Agent 无法完成 G2a**，因为：

1. 需要连接到公司内网 Redshift 集群（需要 VPN）。
2. Redshift 凭证仅存在于公司内部 HashiCorp Vault——Agent 没有 Vault token。
3. 8 条 MRC-relevant SQL 含有动态占位符（`fctrdt`、`service`），必须由了解
   上下文的操作员在执行前替换。

本文的作用：操作员在执行 `freeze_snapshot.py export` 之前阅读本文，完成
§ 7 预飞检查清单，再也不需要翻阅 `PrefectFlow/` 源码。

## 2. 连接配置

### 2.1 连接参数表

| 参数 | 代码来源 | 值 / 说明 |
|---|---|---|
| Cluster identifier | Vault `prefect-secret/db/redshift["hostname"]` | `<cluster-id-redacted>` — 可从公司内部 Vault 路径 `prefect-secret/db/redshift` 的 `hostname` 字段取得；也可查遗留 `flow/config/redshift.yaml`（若可访问）。[VERIFY] |
| Hostname template | 同上 | `<cluster-id-redacted>.<aws-region-redacted>.redshift.amazonaws.com` — 集群 hostname 通过 Vault 注入；AWS Region 待核实。[VERIFY] |
| Port | Vault `prefect-secret/db/redshift["port"]` | 默认 `5439`；实际值由 Vault secret 覆盖。[VERIFY] |
| Database name | `flow/__init__.py:REDSHIFT_DATABASE` | `dev_uat`（UAT 环境）或 `dev`（生产环境）；由 `BUILDENV` 环境变量选择。[FROM-CODE] |
| Schema — MRC remit 表 | `flow/remit_validation/mrc_validation.py` SQL 中硬编码 | `mrc` |
| Schema — port 辅助表 | `flow/__init__.py:REDSHIFT_PORT = "port"` | `port` |
| Driver | `config/db_conn.py:26` | `redshift_connector`（`redshift-connector` Python package） |
| Upload helper | `util/redshift_uploader.py:4` | `pandas_redshift`（通过 S3 中转写入；仅写路径需要，读路径不需要） |
| IAM / federation | — | 未发现 IAM role 代码路径；使用 username + password 认证。[VERIFY] |

> **`BUILDENV` 取值规则**（`cred/settings.py`）：`'uat'` 或 `'test'` → 数据库 `dev_uat`；
> `'prod'` → 数据库 `dev`。MRC 基线快照应在**生产等价环境**中导出，请与系统管理员
> 确认正确的 `BUILDENV` 值。[VERIFY]

### 2.2 连接建立代码路径

```
cred/__init__.py          read_prefect_vault("db/redshift")
  └─ cred/db_cred.py       redshift_cred = RedShiftCred(HOST_NAME, SQL_USER, SQL_PWD, PORT, DATABASE_NAME)
       └─ config/db_conn.py  redshift_connector.connect(host, database, port, user, password)
```

`freeze_snapshot.py export` 在调用 `get_conn(DbTypeEnum.REDSHIFT.value, db)` 时
走上面这条路径（`config/db_conn.py:26-32`）。

## 3. 凭证来源

### 3.1 HashiCorp Vault（主路径 — 唯一受支持路径）

所有 Redshift 凭证经由公司内部 HashiCorp Vault 注入。代码在 `cred/__init__.py`
中使用 `hvac` 客户端。

| 属性 | 值 |
|---|---|
| Vault URL 模板 | `https://<env>-vault.<domain-redacted>` — 其中 `<env>` 由 `BUILDENV` 决定（`test` / `prod`）；`<domain-redacted>` 见 `cred/__init__.py:8`（掩码）。[FROM-CODE] |
| Mount point | `prefect-secret` |
| Secret path | `db/redshift` |
| Keys read | `hostname`、`sql-user`、`sql-pwd`、`port` |
| 认证方式 | Vault token（通过环境变量传入） |

### 3.2 环境变量

| 变量名 | 用途 | 何时使用 |
|---|---|---|
| `BUILDENV` | 选择环境（`uat` / `prod`）；影响 Vault URL 前缀与数据库名 | 始终必须设置 |
| `PREFECT_VAULT_TOKEN` | 通用 Vault token 后备 | 当 env-specific token 未设置时使用 |
| `TEST_PREFECT_VAULT_TOKEN` | UAT / test 环境专用 Vault token | `BUILDENV=uat` 或 `BUILDENV=test` |
| `PROD_PREFECT_VAULT_TOKEN` | 生产环境专用 Vault token | `BUILDENV=prod` |

> `cred/__init__.py:6-7` 中优先级顺序：env-specific token > `PREFECT_VAULT_TOKEN`。

### 3.3 本地配置文件

代码中未发现使用 `~/.aws/credentials` 或本地 `redshift.yaml` 的路径。所有凭证
来自 Vault。若公司内部有 `flow/config/redshift.yaml`，可作为人工备查的参考来
源，但**不被程序读取**。[VERIFY]

### 3.4 AWS Secrets Manager

代码中未发现 AWS Secrets Manager 使用路径（`boto3.client("secretsmanager")`
等调用均未出现在 `flow/remit_validation/` 或 `cred/` 中）。[FROM-CODE]

## 4. MRC 读取的 Schema / 表

以下表格来源：A1 SQL 覆盖扫描（`_export_queries/_coverage.md`）+ 1.1
Raw Data Layer (`1.1-rawdata.zh.md`) § 6 原始表目录。

### 4.1 schema `port`

| 表 | 被哪个 validator 读取 | Filter 列 | 行数估计 | 备注 |
|---|---|---|---|---|
| `port.portmonth` | V1 `mrc_summary_check`、V2 `mrc_adv_validation`、V3 `mrc_general_check`、V4 `mrc_service_fee_check` | `servicer = 'MRC'`、`fctrdt = '2026-05-01'` | [VERIFY] — 约数千行（基线月） | 也被 `get_port_month_data` 读取用于 V2/V3 模板替换后的 CTE `r` |
| `port.portfunding` | V2 `mrc_adv_validation`、V3 `mrc_general_check`、V4 `mrc_service_fee_check` | `loanid` left join | [VERIFY] — 全量读取（`select * from port.portfunding`）；量级待测 | 用于兜底 `dealid`；`get_port_funding_data` 无 WHERE 子句 |
| `port.basic_data_daily_loan_common` | V2 `mrc_adv_validation`、V3 `mrc_general_check` | `servicer = 'MRC'`、`asofdate = '2026-03-31'`（pre month end）或 `'2026-04-30'`（curr month end） | [VERIFY] — 约数千行 × 2 日期切片 | 每个模板在 CTE `p1`（pre）和 `p2`（curr）里各读一次 |
| `port.basic_data_monthly_loan_common` | V3 `mrc_general_check` | `fctrdt = '2026-05-01'`、`servicer = 'MRC'` | [VERIFY] | 用于 `mc.sched_pandi` 兜底计算，left join |

### 4.2 schema `mrc`

| 表 | 被哪个 validator 读取 | Filter 列 | 行数估计 | 备注 |
|---|---|---|---|---|
| `mrc.portmrcremitloanlevelrecap` | V4 `mrc_service_fee_check` | `fctrdt = '2026-05-01'` | [VERIFY] — 约数千行 | 主 JOIN 源 |
| `mrc.portmrcremit3rdpartyadvances` | V5 `mrc_other_check`（经 `_mrc_adv_info_sql`） | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL 的第 1 分支 |
| `mrc.portmrcremitcorpadvances` | V5 `mrc_other_check`（经 `_mrc_adv_info_sql`） | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL 的第 2 分支 |
| `mrc.portmrcremitescrowadvances` | V5 `mrc_other_check`（经 `_mrc_adv_info_sql`） | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL 的第 3 分支 |

> **不直接被 5 个 validator 读取的另外 9 张 `mrc.portmrcremit*` 表**（`portmrcremitdeferredinterest`、
> `portmrcremitinvoices`、`portmrcremitliquidations`、`portmrcremitloanmodification`、
> `portmrcremitpif`、`portmrcremitremittancedetail`、`portmrcremitsupplementalfunds`、
> `portmrcremittrialbalance`、`portmrcremitupbrollforward`）在 G2a 导出计划中**不**
> 需要导出——除非 A2 或 Stage 2 进一步分析证明它们被间接依赖。[FROM-CODE]

## 5. 预期查询延迟与行数

| SQL / 函数 | 预期延迟 | 预期行数 | 说明 |
|---|---|---|---|
| `mrc_summary_check`（V1） | [VERIFY] — 预计 < 5 s | [VERIFY] — 1 行（全量聚合） | `port.portmonth` 单月 MRC aggregate；无 GROUP BY |
| `mrc_service_fee_check`（V4） | [VERIFY] — 预计 < 30 s | [VERIFY] — 约 1–5k 行 | `mrc.portmrcremitloanlevelrecap` 左连两张辅助表 |
| `_mrc_adv_info_sql`（V5） | [VERIFY] — 预计 < 30 s | [VERIFY] — 约 10–200 行 | 3 张 advances 表 UNION ALL，`GROUP BY` 后 |
| `mrc_adv_validation` template（V2） | [VERIFY] — 预计 < 60 s | [VERIFY] — 约 1–5k 行 | 3-CTE 模板，依赖 `port.basic_data_daily_loan_common` × 2 切片 |
| `mrc_general_check` template（V3） | [VERIFY] — 预计 < 60 s | [VERIFY] — 约 1–5k 行 | 3-CTE 模板，同上 + `port.basic_data_monthly_loan_common` |
| `get_port_month_data` | [VERIFY] — 预计 < 30 s | [VERIFY] — 全量 MRC portmonth | 带 SLS 去重 left join，无日期过滤 |
| `get_port_funding_data` | [VERIFY] — 预计 < 30 s | [VERIFY] — 全量 portfunding | `select *`，无过滤 |

> 所有延迟 / 行数均为 [VERIFY]——需要在有 Redshift 访问权限的环境中实测。参考依据：
> 1.1-rawdata.zh.md § 6 确认 5 个 validator 直接读取的表为 6 张（4 个 `mrc.*` + `port.portmonth` + `port.portfunding`）。

## 6. 网络前提条件

| 前提 | 说明 |
|---|---|
| VPN 连接 | 公司内网 VPN 必须处于已连接状态才能到达 Redshift 集群 hostname。[VERIFY — 确认具体 VPN 名称 / 配置] |
| Redshift 安全组入站规则 | 执行机器的 IP 必须在 Redshift 集群安全组的入站规则中。[VERIFY — 联系 infra 团队确认当前白名单规则] |
| Vault 可达性 | `https://<env>-vault.<domain-redacted>` 必须在 VPN 内可达（`cred/__init__.py:8`）。[VERIFY] |
| Jump host | 代码中未发现 SSH 隧道 / jump host 模式；假设可直连。[VERIFY — 若直连不通，联系 infra] |
| S3 访问（仅写路径） | `util/redshift_uploader.py` 使用 S3 中转上传；G2a 导出（只读）不需要此路径。[FROM-CODE] |

## 7. 操作员预飞检查清单

在执行 `python tools/freeze_snapshot.py export --servicer mrc --remit-date 2026-04-30` 之前：

1. **连接 VPN** — 确保公司内网 VPN 已建立，可 ping 通 Redshift hostname。
2. **设置 `BUILDENV`** — `export BUILDENV=prod`（或 `uat`，根据要导出的数据库确认）。
3. **设置 Vault token** — `export PROD_PREFECT_VAULT_TOKEN=<your-token>`（或 `TEST_PREFECT_VAULT_TOKEN` for uat）。确认 token 未过期（`hvac.Client.is_authenticated()` 会在 `cred/__init__.py:11` 做检查）。
4. **验证 Vault 路径可达** — 手动运行：
   ```python
   from cred import read_prefect_vault
   s = read_prefect_vault("db/redshift")
   print(s.keys())  # 应看到 hostname, sql-user, sql-pwd, port
   ```
5. **验证 Redshift 连接** — 手动运行：
   ```python
   from config.db_conn import get_conn
   from cred.settings import DbTypeEnum
   conn = get_conn(DbTypeEnum.REDSHIFT.value, "dev")  # 或 "dev_uat"
   cur = conn.cursor(); cur.execute("select 1"); print(cur.fetchone())
   conn.close()
   ```
6. **确认 `fctrdt` 值** — MRC 基线对应 `fctrdt = '2026-05-01'`（由 `get_fctrdt('2026-04-30')` 计算得出；见 `1.1-rawdata.zh.md` § 3）。
7. **检查 `_plan_index.json`** — 确认 `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_plan_index.json` 存在并包含所有 8 条 MRC-relevant SQL。
8. **确认磁盘空间** — Parquet 输出写入 `baselines/mrc/2026-04-30/input_snapshots/parquet/`；估计总量 [VERIFY]，确保有足够磁盘空间。
9. **在 Git LFS 环境中运行** — `baselines/**/*.parquet` 被 `.gitattributes` 追踪为 LFS 对象；执行机器必须安装 `git-lfs` 并已 `git lfs install`。[VERIFY — 若 LFS 未配置，parquet 文件将作为普通文件提交]

## 8. 本文不能包含的内容

> ⛔ **反模式提醒**：以下内容**绝对不能**出现在本文或任何提交中。

- 真实 Redshift hostname、IP 地址、集群标识符
- 真实 Vault URL 或 Vault token（任何环境）
- 数据库用户名或密码（明文或 Base64）
- 真实 IAM role ARN
- AWS Access Key ID / Secret Access Key
- `~/.aws/credentials` 文件内容截图

如需传递凭证，使用公司内部安全渠道（Vault、Slack DM、1Password）——**不要放进 Git**。

## 9. 参考文献

| 文档 / 文件 | 说明 |
|---|---|
| `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md` | A1 SQL 覆盖扫描输出；列出 8 条 MRC-relevant SQL 及其占位符 |
| `docs/mrc/1.1-rawdata.zh.md` | 1.1 Raw Data Layer — 原始表清单、loader 调用链、时间锚点计算 |
| `docs/mrc/1.2-dataflow.zh.md` | 1.2 Dataflow Layer — SQL template 的 join 拓扑与 CTE 结构 |
| `tools/freeze_snapshot.py` | G2a 导出工具；`plan` 子命令生成 SQL 文件，`export` 子命令执行导出 |
| `cred/__init__.py` | Vault 客户端初始化；Vault URL 模板、token 来源 |
| `cred/db_cred.py` | `RedShiftCred` Pydantic Block；Vault path `db/redshift` |
| `config/db_conn.py:13` | `get_conn()` — `redshift_connector.connect()` 调用 |
| `flow/__init__.py` | `REDSHIFT_PORT = "port"`、`REDSHIFT_DATABASE` 定义 |
| `decisions.md` | 2026-05-17 G2 重定义条目；2026-05-17 G2a A6 条目 |
