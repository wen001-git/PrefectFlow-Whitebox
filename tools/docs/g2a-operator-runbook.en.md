# G2a Operator Runbook — MRC Input Snapshot Freeze

<!-- G2A-A5: OPERATOR-ONLY — Runbook for executing the G2a snapshot export.
     Requires VPN access + HashiCorp Vault token. No agent can satisfy these
     dependencies autonomously. -->
<!-- LIVING-DOC: Update this file whenever tool flags, bindings, or the
     export workflow change. -->

> **Audience**: Any operator (user / colleague / future-Copilot session) who
> needs to execute the G2a export end-to-end.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — G2a A5 initial version. Sources: `tools/freeze_snapshot.py` v2.2, `_coverage.md`, `_bindings.json`, `docs/mrc/_g2a-redshift-dependencies.en.md`. |

---

## 1. Purpose

G2a (the `mrc-snapshot` todo) is the one-time export step that freezes every
Redshift dataset that the 5 MRC validators actually read — into local Parquet
files under `baselines/mrc/2026-04-30/input_snapshots/parquet/` — so that
Stage 2 development can re-run the full MRC validation report with **zero live
Redshift dependency**.

**Why operator-only?** The agent can build tooling and resolve SQL templates,
but it cannot connect to the company's internal Redshift cluster (VPN required)
or read credentials from HashiCorp Vault (no token). The actual SQL execution
against Redshift must be performed by a human who has both.

**Who closes G2a?** The current user, a colleague with Redshift access, or any
future session that has VPN + Vault credentials. After the operator commits the
`_manifest.json` and Parquet files, the agent resumes to drive G2b and G3.

---

## 2. Pre-flight checklist

Work through every item before running any command.

- [ ] **VPN connected** — must be on the company VPN; Redshift cluster is not
      publicly accessible.
- [ ] **Vault token valid** — you can read `prefect-secret/db/redshift`:

  ```bash
  vault kv get prefect-secret/db/redshift
  ```

  If expired, re-auth via your identity provider and export a fresh token:

  ```bash
  export VAULT_TOKEN=$(vault login -method=<your-method> -token-only)
  ```

  Full credential details: see
  [`docs/mrc/_g2a-redshift-dependencies.en.md`](../docs/mrc/_g2a-redshift-dependencies.en.md)
  §§ 2–3.

- [ ] **Python environment** — the following packages must be installed:

  ```bash
  pip install redshift-connector pandas pyarrow hvac
  ```

  Verify:

  ```python
  import redshift_connector, pandas, pyarrow, hvac
  print("all imports OK")
  ```

- [ ] **Repo cloned and up to date** — on `main`, recent pull:

  ```bash
  git checkout main && git pull origin main
  ```

- [ ] **`.env` populated** — copy `.env.example` to `.env` and fill in actual
      values (**never commit `.env`**):

  ```bash
  cp .env.example .env
  # edit .env — set VAULT_ADDR, VAULT_TOKEN, and verify anchor dates
  ```

  See `.env.example` in the project root for the full template.

---

## 3. Step 1 — Generate the export plan

From the project root:

```bash
python tools/freeze_snapshot.py plan \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --resolve
```

### What gets produced

| Output | Location | Description |
|---|---|---|
| Template SQL (all 21 strings) | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/template/*.sql` | Verbatim SQL with `{placeholder}` preserved; every servicer's SQL, not just MRC |
| Resolved SQL (MRC-only, ready to run) | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/resolved/*.sql` | Placeholders replaced with anchor bindings; 9 files for 8 MRC templates (one fan-out) |
| Plan index | `baselines/mrc/2026-04-30/input_snapshots/_plan_index.json` | Machine-readable manifest of all SQL hits; used by `verify` subcommand |
| Coverage report | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md` | Human-readable table; review before exporting |
| Bindings snapshot | `baselines/mrc/2026-04-30/input_snapshots/_bindings.json` | Anchor bindings used for `--resolve`; committed to git |

> **Before proceeding to Step 2**, open `_coverage.md` and confirm the summary
> row reads **"MRC-relevant SQL strings: 8"** and all 5 chapter-1.2 templates
> show ✅.

---

## 4. Step 2 — Review resolved SQL

**Open each file in `_export_queries/resolved/`** and read it before running
anything. There are 9 resolved files:

```
mrc__get_port_funding_data_<sha>.sql
mrc__get_port_month_data_<sha>.sql       (two variants — one with service filter)
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-04-01.sql
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-05-01.sql
mrc__mrc_adv_validation_<sha>.sql
mrc__mrc_general_check_<sha>.sql
mrc__mrc_service_fee_check_<sha>.sql
mrc__mrc_summary_check_<sha>.sql
```

### Binding verification checklist

| Binding | Expected value | What it represents |
|---|---|---|
| `fctrdt` (current month) | `2026-05-01` | Factor date = 1st day of remit month |
| `fctrdt_1m` / prior `fctrdt` | `2026-04-01` | Prior-month factor date |
| `service` | `'MRC'` | Servicer name filter in SQL |
| `remit_date` | `2026-04-30` | Anchor remit date |

- Confirm `WHERE fctrdt = '2026-05-01'` appears in the current-period queries.
- Confirm `WHERE fctrdt = '2026-04-01'` appears in the prior-period queries.
- Confirm `WHERE service = 'MRC'` (or `'mrc'` case-insensitive) appears where
  expected (e.g. `get_port_month_data` variants).
- Confirm no `{expr}` curly-brace placeholders remain in any resolved file.

### Fan-out sanity check

`_mrc_adv_info_sql` must have **exactly 2** resolved variants:

```
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-05-01.sql   ← current cycle
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-04-01.sql   ← prior cycle (MoM delta)
```

This is correct: the validator calls this function twice (once per fctrdt) and
merges the results via a pandas left join to compute month-over-month advance
info deltas. See `docs/mrc/_g2a-redshift-dependencies.en.md` § 4 for the
underlying table details.

---

## 5. Step 3 — Run exports (per dataset)

> **Do NOT create `tools/g2a_export_helper.py` in this repo** — credentials
> must not enter the repo, and the script runs in the operator's local
> environment only. Use the snippet below as a copy-pasteable starting point.

### Copy-pasteable export snippet

Save this as `~/g2a_export_helper.py` (outside the repo) and run it from your
virtual environment after completing the pre-flight checklist.

```python
"""
g2a_export_helper.py — G2a MRC input snapshot exporter.
Run from outside the repo; reads _plan_index.json from the repo path.
Requires: redshift_connector, pandas, pyarrow, hvac, python-dotenv (optional).
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import hvac
import pandas as pd
import redshift_connector

# ── Configuration ──────────────────────────────────────────────────────────────
REPO_ROOT       = Path("/path/to/PrefectFlow-Whitebox")  # ← adjust
SERVICER        = "mrc"
REMIT_DATE      = "2026-04-30"
SNAPSHOT_DIR    = REPO_ROOT / "baselines" / SERVICER / REMIT_DATE / "input_snapshots"
PARQUET_DIR     = SNAPSHOT_DIR / "parquet"
PLAN_INDEX      = SNAPSHOT_DIR / "_plan_index.json"
MANIFEST_PATH   = SNAPSHOT_DIR / "_manifest.json"
RESOLVED_DIR    = SNAPSHOT_DIR / "_export_queries" / "resolved"

VAULT_ADDR      = os.environ["VAULT_ADDR"]
VAULT_TOKEN     = os.environ["VAULT_TOKEN"]
VAULT_RS_PATH   = os.environ.get("VAULT_REDSHIFT_PATH", "prefect-secret/db/redshift")

# ── Vault credential fetch ──────────────────────────────────────────────────────
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
secret = client.secrets.kv.read_secret_version(path=VAULT_RS_PATH)["data"]["data"]
RS_HOST     = secret["hostname"]
RS_PORT     = int(secret.get("port", 5439))
RS_DATABASE = secret["database"]
RS_USER     = secret["username"]
RS_PASSWORD = secret["password"]

# ── Helpers ─────────────────────────────────────────────────────────────────────
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_canonical_rows(df: pd.DataFrame) -> str:
    """Stable hash over sorted (row, col, value) tuples."""
    h = hashlib.sha256()
    for row in df.sort_values(by=list(df.columns)).itertuples(index=False):
        h.update(str(tuple(row)).encode("utf-8"))
    return h.hexdigest()


# ── Load plan index ──────────────────────────────────────────────────────────────
plan_data = json.loads(PLAN_INDEX.read_text(encoding="utf-8"))
entries = [e for e in plan_data["entries"] if e.get("mrc_relevant")]
PARQUET_DIR.mkdir(parents=True, exist_ok=True)

manifest: list[dict] = []

# ── Connect to Redshift ──────────────────────────────────────────────────────────
conn = redshift_connector.connect(
    host=RS_HOST,
    port=RS_PORT,
    database=RS_DATABASE,
    user=RS_USER,
    password=RS_PASSWORD,
)
conn.autocommit = True

# ── Export loop ──────────────────────────────────────────────────────────────────
for entry in entries:
    resolved_paths = entry.get("resolved_paths", [])
    # Fan-out: one resolved file per binding set; non-fan-out: single resolved file
    targets = resolved_paths if resolved_paths else []

    for resolved_rel in targets:
        sql_path = REPO_ROOT / resolved_rel
        if not sql_path.exists():
            raise FileNotFoundError(f"Resolved SQL not found: {sql_path}")

        sql_text = sql_path.read_text(encoding="utf-8")
        # Strip header comment lines (lines starting with --)
        sql_body = "\n".join(
            line for line in sql_text.splitlines()
            if not line.strip().startswith("--")
        ).strip()

        logical_name = sql_path.stem  # filename without .sql
        parquet_path = PARQUET_DIR / f"{logical_name}.parquet"

        print(f"[EXPORT] {logical_name} ... ", end="", flush=True)
        try:
            cursor = conn.cursor()
            cursor.execute(sql_body)
            df = cursor.fetch_dataframe()
            df.to_parquet(parquet_path, index=False, engine="pyarrow")
            cursor.close()

            file_sha = sha256_file(parquet_path)
            row_sha  = sha256_canonical_rows(df)
            col_list = [
                {"name": c, "dtype": str(df[c].dtype)}
                for c in df.columns
            ]
            print(f"{len(df)} rows, {len(df.columns)} cols ✅")

            manifest.append({
                "logical_name":           logical_name,
                "source":                 {"type": "redshift",
                                           "schema": "",   # ← fill from SQL
                                           "table": ""},   # ← fill from SQL
                "export_sql_path":        str(resolved_rel),
                "filter":                 entry.get("filter_hints", {}),
                "exported_at":            datetime.now(tz=timezone.utc).isoformat(),
                "exporter":               RS_USER,
                "format":                 "parquet",
                "path":                   str(parquet_path.relative_to(SNAPSHOT_DIR)),
                "row_count":              len(df),
                "column_count":           len(df.columns),
                "columns":                col_list,
                "sha256_file":            file_sha,
                "sha256_canonical_rows":  row_sha,
                "redshift_session":       {
                    "user":     RS_USER,
                    "cluster":  RS_HOST,
                    "query_id": None,   # Redshift query_id not easily retrievable here
                },
            })

        except Exception as exc:
            print(f"FAILED ❌")
            print(f"  ERROR: {exc}")
            print(f"  SQL path: {sql_path}")
            print("  → Fix the SQL or bindings, then re-run. Do NOT silently skip.")
            raise  # hard stop — never silently skip a failed export

conn.close()

# ── Write manifest ────────────────────────────────────────────────────────────────
MANIFEST_PATH.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False, default=str),
    encoding="utf-8",
)
print(f"\n[DONE] {len(manifest)} entries written to {MANIFEST_PATH}")
```

### Error handling contract

| Situation | Required action |
|---|---|
| SQL execution raises an exception | Print the full error, print the SQL path, **raise** (hard stop). Never silently skip. |
| Resolved SQL file not found | Raise `FileNotFoundError`. Re-run `plan --resolve`. |
| Parquet write fails (disk full, permissions) | Fix the environment issue; re-export the affected dataset. |
| Row count is 0 | Investigate: wrong bindings? wrong date? The verify step (C2) will reject `row_count <= 0`. |

---

## 6. Step 4 — Populate `_manifest.json`

The export snippet in Step 3 writes the manifest progressively. Each entry
must conform to the `MANIFEST_ENTRY_TEMPLATE` in `tools/freeze_snapshot.py`
(around line 208):

```python
MANIFEST_ENTRY_TEMPLATE = {
    "logical_name":          "",          # stem of the resolved SQL filename
    "source":                {            # Redshift source info
        "type":   "redshift",
        "schema": "",                     # e.g. "mrc" or "port"
        "table":  "",                     # primary table queried
    },
    "export_sql_path":       "",          # relative path to the resolved .sql file
    "filter":                {},          # placeholder bindings used (from filter_hints)
    "exported_at":           None,        # ISO-8601 UTC timestamp
    "exporter":              None,        # Redshift username who ran the query
    "format":                "parquet",   # always "parquet"
    "path":                  "",          # path to .parquet file, relative to snapshot dir
    "row_count":             None,        # int > 0
    "column_count":          None,        # int > 0 (must == len(columns))
    "columns":               [],          # [{"name": "col", "dtype": "int64"}, ...]
    "sha256_file":           None,        # sha256 hex of the .parquet file bytes
    "sha256_canonical_rows": None,        # sha256 over sorted (row, col, value) tuples
    "redshift_session":      {
        "user":     None,
        "cluster":  None,
        "query_id": None,
    },
}
```

### Worked example — `mrc_summary_check`

```json
{
  "logical_name":          "mrc__mrc_summary_check_e943649b57cd",
  "source":                {"type": "redshift", "schema": "mrc",
                            "table": "portmrcremitloanlevelrecap"},
  "export_sql_path":       "_export_queries/resolved/mrc__mrc_summary_check_e943649b57cd.sql",
  "filter":                {"mrc_db.fctrdt": "2026-05-01"},
  "exported_at":           "2026-05-18T09:42:00Z",
  "exporter":              "your-redshift-username",
  "format":                "parquet",
  "path":                  "parquet/mrc__mrc_summary_check_e943649b57cd.parquet",
  "row_count":             1,
  "column_count":          5,
  "columns": [
    {"name": "tot_uupb",      "dtype": "float64"},
    {"name": "tot_remit_amt", "dtype": "float64"},
    {"name": "tot_curtailment","dtype":"float64"},
    {"name": "tot_svcfee",    "dtype": "float64"},
    {"name": "tot_int",       "dtype": "float64"}
  ],
  "sha256_file":           "a1b2c3d4...e5f6 (64 hex chars)",
  "sha256_canonical_rows": "9f8e7d6c...5b4a (64 hex chars)",
  "redshift_session":      {"user": "your-redshift-username",
                            "cluster": "<cluster-id>.redshift.amazonaws.com",
                            "query_id": null}
}
```

> **Tip**: the export snippet writes entries progressively — if a query fails
> mid-run, already-exported entries are safe in the partially-written manifest.
> Fix the failing SQL, remove the partial manifest entry for that dataset, and
> re-run only the affected query.

---

## 7. Step 5 — Verify

```bash
python tools/freeze_snapshot.py verify \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --strict \
    --verbose \
    --json
```

### Exit codes

| Code | Meaning | Action |
|---|---|---|
| `0` | All checks passed (core C1–C6 + strict C7–C8) | Proceed to Step 6 |
| `1` | One or more **core** checks (C1–C6) failed | Read `_verify_report.json`; fix and re-export |
| `2` | Core passed, but **strict-only** check(s) failed (C7–C8) | Read `_verify_report.json`; decide whether to fix before hand-off |

### Check summary

| Check | What it validates |
|---|---|
| C1 — coverage parity | Every expected dataset is in the manifest; no orphan entries |
| C2 — schema completeness | All required fields present, row_count > 0, sha256 format valid |
| C3 — file + checksum | Parquet file exists on disk; sha256 matches manifest value |
| C4 — SQL hash binding | Optional `sql_sha256` field matches the resolved SQL file (if provided) |
| C5 — schema sanity | `column_count` == `len(columns)`; no duplicate column names; no empty dtypes |
| C6 — fan-out consistency | `_mrc_adv_info_sql` has exactly 2 manifest entries (one per fctrdt) |
| C7 — bindings doc [strict] | `_bindings.json` exists and is consistent |
| C8 — storage policy [strict] | Parquet files are in the expected path; `.gitignore` policy respected |

### If verify fails

1. Run with `--json` to get `_verify_report.json`.
2. Open the report and read the `"details"` arrays under each failing check.
3. Apply the fix described in §10 Troubleshooting.
4. Re-run verify until exit code is `0` (or `2` if you accept the strict delta).

---

## 8. Step 6 — Hand-off back to the agent

### Commit the artifacts

```bash
git add baselines/mrc/2026-04-30/input_snapshots/_manifest.json
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/template/
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/resolved/
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md
git add baselines/mrc/2026-04-30/input_snapshots/_verify_report.json
git commit -m "g2a(export): MRC 2026-04-30 input snapshot — <N> datasets

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push origin main
```

> **Note on `_plan_index.json`**: this file is typically already committed from
> the A1/A3 tooling step. If you re-ran `plan --resolve`, re-commit it too.

### Parquet files — Git LFS / out-of-band storage

Per `.gitignore`, Parquet files under
`baselines/**/input_snapshots/parquet/` are **not committed to git directly**.
Before committing, confirm with the team which storage option applies:

- **Git LFS** (default plan): `git lfs track "baselines/**/*.parquet"` then
  `git add .gitattributes` then add the parquet files normally.
- **Out-of-band shared storage** (e.g. S3, SharePoint): upload the Parquet
  files to the agreed location and record the URL in each manifest entry's
  `"path"` field.

### Notify the agent

After pushing, update `plan.md` or post a session message:

> "G2a closed; all 9 Parquet files exported and verified.
>  Agent please proceed with G2b."

The agent will then drive `mrc-source-baseline` + `mrc-gold` (G2b).

---

## 9. Credentials do-not-commit checklist

Before every `git add` / `git commit`, confirm:

- [ ] No Vault tokens in any staged file.
- [ ] No real Redshift hostnames in commits — use `<cluster-id-redacted>` or
      leave the `redshift_session.cluster` field as the hostname only if that
      is acceptable to your organization's security policy.
- [ ] `.env` is in `.gitignore` (it is — verified in project `.gitignore`).
- [ ] The export helper script (`~/g2a_export_helper.py`) is **outside the
      repo** and is not staged.
- [ ] `_manifest.json` contains only the Redshift **username** and
      cluster hostname from `redshift_session`, not the password.

### Optional: pre-commit hook

Add this to `.git/hooks/pre-commit` to catch accidental token leaks:

```bash
#!/bin/sh
if git diff --cached --name-only | xargs grep -l "VAULT_TOKEN\|hvs\.\|password" 2>/dev/null; then
    echo "ERROR: Possible secret detected in staged files. Aborting commit."
    exit 1
fi
```

---

## 10. Troubleshooting

### Vault token expired

```
Error authenticating: 403 Forbidden
```

Re-auth and export a fresh token:

```bash
vault login -method=<your-method>
export VAULT_TOKEN=$(vault print token)
```

### SQL placeholder not resolved

If a resolved file still contains `{expr}` braces:

1. Check `baselines/mrc/2026-04-30/input_snapshots/_bindings.json` — is the
   placeholder key listed under `"bindings"`?
2. Re-run `python tools/freeze_snapshot.py plan --servicer mrc --remit-date 2026-04-30 --resolve`.
3. If the placeholder is genuinely unknown, add it to `_bindings.json` before
   re-running (or pass a custom `--bindings` file).

### Verify fails C3 — checksum mismatch

```
C3-file-existence-checksum: sha256_file mismatch (expected a1b2c3d4…, got 9f8e7d6c…)
```

The Parquet file was modified after the manifest was written (e.g. re-exported
without updating the manifest). Fix: re-export the affected dataset so the
Parquet file and manifest entry are consistent.

### Verify fails C6 — fan-out inconsistency

```
C6-fanout-consistency: _mrc_adv_info_sql has 1 manifest entry (expected 2)
```

The `_mrc_adv_info_sql` query must be exported **twice** — once with
`fctrdt=2026-05-01` and once with `fctrdt=2026-04-01`. Both variants must
appear in `_manifest.json` with distinct `logical_name` values. Export the
missing variant and add its entry to the manifest.

### Verify fails C1 — orphan manifest entry

```
C1-coverage-parity: Orphan in manifest (1): some_unexpected_name
```

The manifest contains an entry that does not correspond to any expected dataset
(not in `_plan_index.json`'s MRC-relevant list). Either remove the orphan entry
from the manifest, or re-run `plan --resolve` if the coverage scan was updated
to include a new template.

### Verify fails C2 — `row_count <= 0`

The query returned 0 rows. Possible causes:
- Wrong `fctrdt` binding — confirm the date against your Redshift data.
- Wrong `service` filter — confirm `'MRC'` is the right case.
- The table was empty for this cycle — confirm with the data team.

---

## 11. References

- **A6 Redshift dependency catalog** (tables, schemas, credential paths):
  [`docs/mrc/_g2a-redshift-dependencies.en.md`](../docs/mrc/_g2a-redshift-dependencies.en.md)
- **SQL coverage report**: `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md`
- **Decisions log** (G2 redefinition, A1–A6 entries):
  `decisions.md` — search `"G2a"` or `"G2 redefinition"`
- **Plan § 4.2** (G2a binding spec):
  `C:\Users\jli\.copilot\session-state\4cd52a8e-d034-4def-84a0-04057dd64872\plan.md`
  § 4.2 "G2a — frozen input snapshot specification (binding)"
