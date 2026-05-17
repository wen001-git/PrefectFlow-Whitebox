# _G2a A6 — Redshift Dependency Catalog

<!-- G2A-A6: OPERATOR-ONLY — This file enumerates all Redshift access prerequisites for running the G2a snapshot export. An agent cannot independently satisfy these dependencies; a human operator with VPN access and a Vault token must execute the export. -->
<!-- LIVING-DOC: Update this file whenever connection parameters, credential paths, or queried tables change. -->

> **Purpose**: The G2a snapshot export (`tools/freeze_snapshot.py export`) is an
> **operator-only** operation — it requires Redshift VPN access and a HashiCorp
> Vault token. This file is a single-document prerequisite checklist so any operator
> (the current user, a colleague, or a future Copilot session) can know exactly
> what Redshift access is required to execute G2a — without spelunking the source repo.
>
> **Audience**: Operators with Redshift access; the next agent resuming G2a work.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — G2a A6 initial version. Sources: `cred/__init__.py`, `cred/db_cred.py`, `config/db_conn.py`, `flow/__init__.py`, `_export_queries/_coverage.md`, `docs/mrc/1.1-rawdata.en.md`. |

---

## 1. Why this file exists

G2a (the `mrc-snapshot` todo) aims to export every Redshift dataset that the
5 MRC validators actually read — into Parquet files under
`baselines/mrc/2026-04-30/input_snapshots/parquet/` — so the Stage 2
Parquet-reading shim can re-run the validation report with **zero live Redshift
dependency**.

**An agent cannot complete G2a** because:

1. It requires connecting to the company's internal-network Redshift cluster (VPN required).
2. Redshift credentials exist only in the company's internal HashiCorp Vault — the agent has no Vault token.
3. The 8 MRC-relevant SQL strings contain dynamic placeholders (`fctrdt`, `service`) that must be resolved by an operator who understands the context.

This document's role: read it before running `freeze_snapshot.py export`, complete the § 7 pre-flight checklist, and proceed without needing to consult `PrefectFlow/` source code.

## 2. Connection profile

### 2.1 Connection parameters table

| Parameter | Code source | Value / notes |
|---|---|---|
| Cluster identifier | Vault `prefect-secret/db/redshift["hostname"]` | `<cluster-id-redacted>` — obtain from Vault path `prefect-secret/db/redshift`, key `hostname`; also check legacy `flow/config/redshift.yaml` if accessible. [VERIFY] |
| Hostname template | Same as above | `<cluster-id-redacted>.<aws-region-redacted>.redshift.amazonaws.com` — injected via Vault; AWS Region to be confirmed. [VERIFY] |
| Port | Vault `prefect-secret/db/redshift["port"]` | Default `5439`; actual value overridden by Vault secret. [VERIFY] |
| Database name | `flow/__init__.py:REDSHIFT_DATABASE` | `dev_uat` (UAT) or `dev` (prod); selected by `BUILDENV` env var. [FROM-CODE] |
| Schema — MRC remit tables | Hard-coded in SQL strings in `flow/remit_validation/mrc_validation.py` | `mrc` |
| Schema — port auxiliary tables | `flow/__init__.py:REDSHIFT_PORT = "port"` | `port` |
| Driver | `config/db_conn.py:26` | `redshift_connector` (Python `redshift-connector` package) |
| Upload helper | `util/redshift_uploader.py:4` | `pandas_redshift` (write path via S3 staging — read-only G2a export does not need this) |
| IAM / federation | — | No IAM role code path found; username + password authentication used. [VERIFY] |

> **`BUILDENV` selection rule** (`cred/settings.py`): `'uat'` or `'test'` → database `dev_uat`;
> `'prod'` → database `dev`. The MRC baseline snapshot should be exported from a
> production-equivalent environment; confirm the correct `BUILDENV` value with your
> system administrator. [VERIFY]

### 2.2 Connection code path

```
cred/__init__.py          read_prefect_vault("db/redshift")
  └─ cred/db_cred.py       redshift_cred = RedShiftCred(HOST_NAME, SQL_USER, SQL_PWD, PORT, DATABASE_NAME)
       └─ config/db_conn.py  redshift_connector.connect(host, database, port, user, password)
```

`freeze_snapshot.py export` calls `get_conn(DbTypeEnum.REDSHIFT.value, db)`, which
follows the path above (`config/db_conn.py:26-32`).

## 3. Credential sources

### 3.1 HashiCorp Vault (primary — only supported path)

All Redshift credentials are injected via the company's internal HashiCorp Vault.
The code uses the `hvac` client in `cred/__init__.py`.

| Attribute | Value |
|---|---|
| Vault URL template | `https://<env>-vault.<domain-redacted>` — where `<env>` is `test` or `prod` based on `BUILDENV`; `<domain-redacted>` is the company domain visible in `cred/__init__.py:8` (masked here). [FROM-CODE] |
| Mount point | `prefect-secret` |
| Secret path | `db/redshift` |
| Keys read | `hostname`, `sql-user`, `sql-pwd`, `port` |
| Authentication method | Vault token (passed via environment variable) |

### 3.2 Environment variables

| Variable | Purpose | When used |
|---|---|---|
| `BUILDENV` | Select environment (`uat` / `prod`); affects Vault URL prefix and database name | Must always be set |
| `PREFECT_VAULT_TOKEN` | Generic fallback Vault token | When env-specific token is not set |
| `TEST_PREFECT_VAULT_TOKEN` | UAT / test environment Vault token | `BUILDENV=uat` or `BUILDENV=test` |
| `PROD_PREFECT_VAULT_TOKEN` | Production environment Vault token | `BUILDENV=prod` |

> Priority in `cred/__init__.py:6-7`: env-specific token takes precedence over `PREFECT_VAULT_TOKEN`.

### 3.3 Local config files

No usage of `~/.aws/credentials` or a local `redshift.yaml` was found in the
code. All credentials come from Vault. If the company maintains a
`flow/config/redshift.yaml`, it can serve as a human reference but is
**not read programmatically**. [VERIFY]

### 3.4 AWS Secrets Manager

No AWS Secrets Manager code path was found (`boto3.client("secretsmanager")`
calls do not appear in `flow/remit_validation/` or `cred/`). [FROM-CODE]

## 4. Schemas and tables consumed by MRC validators

The tables below are sourced from: A1 SQL coverage scan (`_export_queries/_coverage.md`)
and the 1.1 Raw Data Layer inventory (`1.1-rawdata.en.md` § 6).

### 4.1 Schema `port`

| Table | Read by validator | Filter columns | Row-count estimate | Notes |
|---|---|---|---|---|
| `port.portmonth` | V1 `mrc_summary_check`, V2 `mrc_adv_validation`, V3 `mrc_general_check`, V4 `mrc_service_fee_check` | `servicer = 'MRC'`, `fctrdt = '2026-05-01'` | [VERIFY] — ~thousands (baseline month) | Also read by `get_port_month_data` for the CTE `r` in V2/V3 templates |
| `port.portfunding` | V2 `mrc_adv_validation`, V3 `mrc_general_check`, V4 `mrc_service_fee_check` | `loanid` left join (no WHERE) | [VERIFY] — full table scan (`select *`); scale unknown | Used to fill in `dealid` fallback; `get_port_funding_data` has no WHERE clause |
| `port.basic_data_daily_loan_common` | V2 `mrc_adv_validation`, V3 `mrc_general_check` | `servicer = 'MRC'`, `asofdate = '2026-03-31'` (pre) or `'2026-04-30'` (curr) | [VERIFY] — ~thousands × 2 date slices | Each template reads it twice in CTEs `p1` (pre month end) and `p2` (curr month end) |
| `port.basic_data_monthly_loan_common` | V3 `mrc_general_check` | `fctrdt = '2026-05-01'`, `servicer = 'MRC'` | [VERIFY] | Used for `mc.sched_pandi` fallback in left join |

### 4.2 Schema `mrc`

| Table | Read by validator | Filter columns | Row-count estimate | Notes |
|---|---|---|---|---|
| `mrc.portmrcremitloanlevelrecap` | V4 `mrc_service_fee_check` | `fctrdt = '2026-05-01'` | [VERIFY] — ~thousands | Primary join source |
| `mrc.portmrcremit3rdpartyadvances` | V5 `mrc_other_check` (via `_mrc_adv_info_sql`) | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL branch 1 |
| `mrc.portmrcremitcorpadvances` | V5 `mrc_other_check` (via `_mrc_adv_info_sql`) | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL branch 2 |
| `mrc.portmrcremitescrowadvances` | V5 `mrc_other_check` (via `_mrc_adv_info_sql`) | `fctrdt = '2026-05-01'` | [VERIFY] | UNION ALL branch 3 |

> **Nine additional `mrc.portmrcremit*` tables** (`portmrcremitdeferredinterest`,
> `portmrcremitinvoices`, `portmrcremitliquidations`, `portmrcremitloanmodification`,
> `portmrcremitpif`, `portmrcremitremittancedetail`, `portmrcremitsupplementalfunds`,
> `portmrcremittrialbalance`, `portmrcremitupbrollforward`) are **not** directly read
> by the 5 validators and do **not** need to be exported in G2a — unless A2 or
> Stage 2 analysis reveals an indirect dependency. [FROM-CODE]

## 5. Expected query latency and row counts

| SQL / function | Expected latency | Expected row count | Notes |
|---|---|---|---|
| `mrc_summary_check` (V1) | [VERIFY] — estimate < 5 s | [VERIFY] — 1 row (full aggregate) | `port.portmonth` single-month MRC aggregate; no GROUP BY |
| `mrc_service_fee_check` (V4) | [VERIFY] — estimate < 30 s | [VERIFY] — ~1–5k rows | `mrc.portmrcremitloanlevelrecap` left-joined with two auxiliary tables |
| `_mrc_adv_info_sql` (V5) | [VERIFY] — estimate < 30 s | [VERIFY] — ~10–200 rows | 3-table UNION ALL, grouped by description + tran_code |
| `mrc_adv_validation` template (V2) | [VERIFY] — estimate < 60 s | [VERIFY] — ~1–5k rows | 3-CTE template; depends on `port.basic_data_daily_loan_common` × 2 date slices |
| `mrc_general_check` template (V3) | [VERIFY] — estimate < 60 s | [VERIFY] — ~1–5k rows | 3-CTE template; same as V2 plus `port.basic_data_monthly_loan_common` |
| `get_port_month_data` | [VERIFY] — estimate < 30 s | [VERIFY] — full MRC portmonth | Includes SLS dedup left join; no date filter |
| `get_port_funding_data` | [VERIFY] — estimate < 30 s | [VERIFY] — full portfunding table | `select *`, no filter |

> All latency / row-count estimates are [VERIFY] — they must be confirmed in an
> environment with live Redshift access. The 1.1-rawdata chapter (§ 6) confirms
> the 6 tables directly read by the 5 validators.

## 6. Network prerequisites

| Prerequisite | Notes |
|---|---|
| VPN connection | Company intranet VPN must be connected to reach the Redshift cluster hostname. [VERIFY — confirm VPN profile name / configuration with infra team] |
| Redshift security-group inbound rule | The executing machine's IP must be in the Redshift cluster's security-group inbound allow-list. [VERIFY — contact infra team to confirm the current whitelist] |
| Vault reachability | `https://<env>-vault.<domain-redacted>` must be reachable from within the VPN (`cred/__init__.py:8`). [VERIFY] |
| Jump host | No SSH tunnel or jump-host pattern was found in code; direct connection assumed. [VERIFY — if direct connection fails, contact infra] |
| S3 access (write path only) | `util/redshift_uploader.py` uses S3 staging for uploads; G2a export (read-only) does not need this path. [FROM-CODE] |

## 7. Operator pre-flight checklist

Before running `python tools/freeze_snapshot.py export --servicer mrc --remit-date 2026-04-30`:

1. **Connect VPN** — ensure the company intranet VPN is established and you can resolve the Redshift hostname.
2. **Set `BUILDENV`** — `export BUILDENV=prod` (or `uat` — confirm which database holds the 2026-04-30 data with your system administrator).
3. **Set Vault token** — `export PROD_PREFECT_VAULT_TOKEN=<replace-with-actual>` (or `TEST_PREFECT_VAULT_TOKEN` for UAT). Verify the token is not expired — `cred/__init__.py:11` calls `hvac.Client.is_authenticated()` and raises if not.
4. **Verify Vault connectivity** — run manually:
   ```python
   from cred import read_prefect_vault
   s = read_prefect_vault("db/redshift")
   print(s.keys())  # expect: hostname, sql-user, sql-pwd, port
   ```
5. **Verify Redshift connection** — run manually:
   ```python
   from config.db_conn import get_conn
   from cred.settings import DbTypeEnum
   conn = get_conn(DbTypeEnum.REDSHIFT.value, "dev")  # or "dev_uat"
   cur = conn.cursor(); cur.execute("select 1"); print(cur.fetchone())
   conn.close()
   ```
6. **Confirm `fctrdt` value** — for MRC baseline `remit_date = 2026-04-30`, `fctrdt = '2026-05-01'` (computed by `get_fctrdt('2026-04-30')`; see `1.1-rawdata.en.md` § 3).
7. **Check `_plan_index.json`** — confirm `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_plan_index.json` exists and contains all 8 MRC-relevant SQL entries.
8. **Confirm disk space** — Parquet output goes to `baselines/mrc/2026-04-30/input_snapshots/parquet/`; total volume is [VERIFY] — ensure sufficient disk space before exporting.
9. **Run in a Git LFS environment** — `baselines/**/*.parquet` is tracked as a Git LFS object in `.gitattributes`; the executing machine must have `git-lfs` installed and `git lfs install` completed. [VERIFY — if LFS is not configured, parquet files will be committed as regular objects]

## 8. What CANNOT be in this file

> ⛔ **Anti-pattern reminder**: The following must **never** appear in this file or any
> commit to this repository.

- Real Redshift hostname, IP address, or cluster identifier
- Real Vault URL or Vault token (any environment)
- Database username or password (plain text or Base64)
- Real IAM role ARN
- AWS Access Key ID or Secret Access Key
- Screenshots or pastes of `~/.aws/credentials`

To share credentials, use the company's secure channels (Vault, Slack DM, 1Password) — **never commit to Git**.

## 9. References

| Document / file | Description |
|---|---|
| `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md` | A1 SQL coverage scan output; lists 8 MRC-relevant SQL strings with their placeholders |
| `docs/mrc/1.1-rawdata.en.md` | 1.1 Raw Data Layer — raw table inventory, loader call chain, time anchor calculations |
| `docs/mrc/1.2-dataflow.en.md` | 1.2 Dataflow Layer — SQL template join topology and CTE structure |
| `tools/freeze_snapshot.py` | G2a export tool; `plan` sub-command generates SQL files, `export` sub-command executes the export |
| `cred/__init__.py` | Vault client initialization; Vault URL template, token source |
| `cred/db_cred.py` | `RedShiftCred` Pydantic Block; Vault path `db/redshift` |
| `config/db_conn.py:13` | `get_conn()` — `redshift_connector.connect()` call |
| `flow/__init__.py` | `REDSHIFT_PORT = "port"`, `REDSHIFT_DATABASE` definition |
| `decisions.md` | 2026-05-17 G2 redefinition entry; 2026-05-17 G2a A6 entry |
