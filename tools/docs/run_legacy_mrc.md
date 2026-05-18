# Legacy MRC Validation Runner — Operator Guide

<!-- LIVING-DOC: Update this file whenever tool flags, credential paths, or
     the legacy entrypoint signature changes. -->

> **Purpose**: Step-by-step guide for operators who need to run the **legacy**
> `remit_validation_check` flow against live Redshift and capture its XLSX
> output alongside a structured JSON metadata sidecar. This is the Round 2 C2
> runner; it does not replace the new whitebox engine — it exists to produce
> live legacy output for side-by-side comparison.
>
> **Intended audience**: Operators with VPN access + a valid HashiCorp Vault
> token who need to generate a reference legacy validation report.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — initial version (Round 2 C2). |

---

## 1. Purpose

`tools/run_legacy_mrc.py` is an **operator-invoked** wrapper around the
original `flow/remit_validation/remit_validation.py` Prefect flow in the
`PrefectFlow` source repository.  It:

1. Loads Vault credentials from a local `.env` file (never committed to git).
2. Invokes `remit_validation_check(remit_date=…)` against live Redshift via
   the existing `cred/` + `config/` credential stack.
3. Captures the produced XLSX validation report.
4. Writes a `run_metadata.json` sidecar recording timestamps, source SHA,
   masked Redshift connection details, and per-MRC-dataset row counts.

**Key property**: the tool itself adds zero new Redshift logic — it is a
transparent pass-through.  All SQL is executed by the legacy code.

---

## 2. Prerequisites

### 2.1 References

| Document | What it covers |
|---|---|
| [`docs/mrc/_g2a-redshift-dependencies.en.md`](../../docs/mrc/_g2a-redshift-dependencies.en.md) | Full Redshift connection profile, Vault path, env-var names, network prerequisites (A6 catalog) |
| [`tools/docs/g2a-operator-runbook.en.md`](g2a-operator-runbook.en.md) | G2a snapshot-freeze runbook (Vault pre-flight steps, connection verification) |

### 2.2 Checklist

- [ ] **VPN connected** — Redshift cluster is not publicly accessible.
- [ ] **Vault token valid** — verify with:
  ```bash
  vault kv get prefect-secret/db/redshift
  ```
- [ ] **Python environment ready** — install required packages:
  ```bash
  pip install redshift-connector pandas openpyxl hvac prefect
  # also install all PrefectFlow/requirements.txt dependencies
  ```
- [ ] **`.env` file populated** — see §3 below.
- [ ] **Source repo present** — `PrefectFlow/` checkout at `../PrefectFlow`
      (or pass `--source-repo`).

### 2.3 Populate `.env`

Copy `.env.example` to `.env` (never commit `.env`):

```bash
cp .env.example .env
```

Then fill in actual values:

```dotenv
VAULT_ADDR=https://<env>-vault.<company-domain>:8200
VAULT_TOKEN=<your-vault-token>
VAULT_REDSHIFT_PATH=prefect-secret/db/redshift
BUILDENV=prod          # or: uat / test
```

`BUILDENV` controls which database the legacy code targets
(`dev` for prod, `dev_uat` for uat/test) and which Vault token env-var the
`cred/` layer reads (`PROD_PREFECT_VAULT_TOKEN` vs `TEST_PREFECT_VAULT_TOKEN`).
The wrapper sets these automatically from `VAULT_TOKEN`.

---

## 3. Example invocation

```bash
# Full live run for remit date 2026-04-30
python tools/run_legacy_mrc.py \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --out-dir runs/legacy/2026-04-30/ \
    --source-repo ../PrefectFlow
```

**Exit codes**

| Code | Meaning |
|---|---|
| `0` | Success — `validation_report.xlsx` produced |
| `1` | Legacy flow failed (check `run.log`) |
| `2` | Credentials / `.env` problem |
| `3` | Source repo not found or `mrc_validation.py` missing |

---

## 4. Dry-run usage

Use `--dry-run` to verify configuration without touching Redshift.  It works
even when `hvac`, `redshift-connector`, and `prefect` are not installed:

```bash
python tools/run_legacy_mrc.py \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --out-dir runs/legacy/test/ \
    --dry-run
```

Sample output:

```
=== DRY-RUN MODE — no Redshift contact ===
  .env loaded from       : .env (found)
  VAULT_ADDR             : https://prod-vault.example.com:8200
  VAULT_REDSHIFT_PATH    : prefect-secret/db/redshift
  BUILDENV               : prod
  Vault token (masked)   : te****
  Source repo            : C:\...\PrefectFlow
  Entrypoint file        : C:\...\PrefectFlow\flow\remit_validation\remit_validation.py
  Entrypoint function    : remit_validation_check(
                               remit_date=datetime.date(2026, 4, 30),
                               email=False, to_new_redshift=True, to_mysql=False)
  date_path              : 20260430
  servicer               : mrc
  out_dir                : runs/legacy/test
  Output XLSX            : runs/legacy/test\validation_report.xlsx
  Run log                : runs/legacy/test\run.log
  Metadata sidecar       : runs/legacy/test\run_metadata.json
```

Returns exit `0` if the plan is coherent (source repo exists, entrypoint file
found, env looks populated).

---

## 5. Output layout

After a successful run, `--out-dir` contains:

```
runs/legacy/2026-04-30/
├── validation_report.xlsx      ← copy of the XLSX produced by the legacy flow
├── run.log                     ← captured stdout + stderr from the flow
├── run_metadata.json           ← structured metadata sidecar
└── xlsx_output/                ← working directory used during run (can be removed)
    └── 20260430/
        └── 2026-04-30_validation_report.xlsx
```

### `run_metadata.json` schema

```json
{
  "tool_version": "1.0.0",
  "started_at": "<ISO-8601 UTC>",
  "finished_at": "<ISO-8601 UTC>",
  "duration_sec": 123.4,
  "servicer": "mrc",
  "remit_date": "2026-04-30",
  "source_repo_path": "<abs path>",
  "source_repo_sha": "<git SHA>",
  "source_repo_dirty": false,
  "python_version": "3.10.x",
  "platform": "Windows-...",
  "redshift": {
    "vault_path": "prefect-secret/db/redshift",
    "user": "us****",
    "cluster": "cl****"
  },
  "output": {
    "xlsx_path": "<abs path>",
    "sha256": "<hex>",
    "size_bytes": 123456
  },
  "datasets": [
    { "name": "mrc_summary_check",    "row_count": 1,   "query_sec": null },
    { "name": "mrc_general_check",    "row_count": 42,  "query_sec": null },
    { "name": "mrc_adv_check",        "row_count": 38,  "query_sec": null },
    { "name": "mrc_service_fee_check","row_count": 1250,"query_sec": null },
    { "name": "mrc_adv_info",         "row_count": 15,  "query_sec": null }
  ],
  "exit_code": 0
}
```

> **Note**: `query_sec` fields are `null` in v1.0 — per-query timing requires
> instrumenting the legacy Redshift connection layer and is deferred to a
> future round.  Row counts are captured from `VALIDATION_TABLE_MAP` after the
> flow completes.

**Credential masking**: `user` and `cluster` always appear masked (first two
characters + `****`).  Real values are never written to this file.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Exit 2: `.env file not found` | `.env` missing in CWD | `cp .env.example .env` then fill in values |
| Exit 2: `VAULT_ADDR and VAULT_TOKEN must be set` | Env vars missing | Check `.env` has `VAULT_ADDR=` and `VAULT_TOKEN=` |
| Exit 3: `Source repo not found` | `--source-repo` path wrong | Point to your local `PrefectFlow` checkout |
| Exit 3: `mrc_validation.py not found` | Wrong repo or different branch | Verify `flow/remit_validation/mrc_validation.py` exists in the source repo |
| Exit 1: `Vault authentication failed` | Token expired | Re-auth: `vault login …` and update `VAULT_TOKEN` in `.env` |
| Exit 1: `redshift_connector` import error | Package not installed | `pip install redshift-connector` (requires VPN for pip if internal mirror) |
| Exit 1: `prefect` import error | Prefect not installed | `pip install prefect` + all `PrefectFlow/requirements.txt` deps |
| Exit 1: `EmptyDataException` in `run.log` | No data for this `remit_date` in Redshift | Confirm the `fctrdt` (= first day of next month) has loaded data; check `BUILDENV` value |
| XLSX produced but has blank sheets | Upstream task returned `None` | Check `run.log` for `ERROR` lines from individual validators |
| `WARNING: hvac not installed` | `hvac` package missing | `pip install hvac` — the Vault pre-check is skipped but legacy code may still authenticate if its own Vault env-vars are set |

For persistent failures, share `run_metadata.json` and the tail of `run.log`
with the team (never share the raw `.env` file — use secure channels instead).
