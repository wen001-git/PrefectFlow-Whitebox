"""Freeze MRC source tables from Redshift to local Parquet.

Mirrors `PrefectFlow-LearningLog/scripts/run_remit_validation.py`: prepends the
read-only PrefectFlow repo to sys.path, loads its `.env` (for
PREFECT_VAULT_TOKEN), and reuses `MrcDB.run_sql` (which goes through
`config.db_conn.get_conn` + `cred.db_cred.redshift_cred`) so we get the same
Redshift connection used by the production flow.

Output layout:
    snapshots/<remit_date>/raw/mrc/<table>.parquet
    snapshots/<remit_date>/raw/mrc/_manifest.json

The manifest records the exact SQL + row count + sha256 of each Parquet so the
snapshot is self-describing for the harness (used by mrc-source-baseline and
mrc-vN-impl diff jobs).

Why MRC-specific (not a generic freezer):
  Each servicer has its own table set + WHERE-clause patterns (some by fctrdt,
  some by asofdate, some by snap_shot_date). One module per servicer keeps each
  manifest readable. Other servicers will get sibling `snapshot_<servicer>.py`
  scripts later.

USAGE (must run from PrefectFlow's venv, where redshift_connector + cred/
modules are installed):

    cd C:\\Users\\jli\\MyData\\Copilot\\PrefectFlow
    .\\.venv\\Scripts\\Activate.ps1
    $env:PYTHONPATH = 'C:\\Users\\jli\\MyData\\Copilot\\PrefectFlow-Whitebox'
    python -m tools.snapshot_mrc 2026-04-30

Or non-default output dir:
    python -m tools.snapshot_mrc 2026-04-30 --out C:\\path\\to\\out
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

PREFECT_FLOW_ROOT = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow")
WHITEBOX_ROOT = Path(__file__).resolve().parent.parent


def _bootstrap_prefect_env() -> None:
    if str(PREFECT_FLOW_ROOT) not in sys.path:
        sys.path.insert(0, str(PREFECT_FLOW_ROOT))
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]
        load_dotenv(PREFECT_FLOW_ROOT / ".env")
    except Exception as e:
        print(f"[snapshot_mrc] dotenv load skipped: {e}")
    if not (os.getenv("PREFECT_VAULT_TOKEN") or os.getenv("TEST_PREFECT_VAULT_TOKEN")):
        raise SystemExit(
            "PREFECT_VAULT_TOKEN missing. Set it in your shell or in "
            f"{PREFECT_FLOW_ROOT}\\.env before running."
        )


def _build_mrc_manifest(fctrdt: str, fctrdt_1m: str, remit_date: str, pre_date: str) -> list[dict[str, str]]:
    """Return a list of {table, sql, where} dicts describing the snapshot."""
    return [
        {
            "table": "port_portmonth_mrc",
            "source": "port.portmonth",
            "where": f"servicer='MRC' AND fctrdt IN ('{fctrdt}', '{fctrdt_1m}')",
            "sql": (
                "SELECT * FROM port.portmonth "
                f"WHERE servicer = 'MRC' AND fctrdt IN ('{fctrdt}', '{fctrdt_1m}');"
            ),
        },
        {
            "table": "port_portfunding_mrc",
            "source": "port.portfunding",
            "where": "loanid IN (SELECT loanid FROM port.portmonth WHERE servicer='MRC')",
            "sql": (
                "SELECT f.* FROM port.portfunding f "
                "WHERE f.loanid IN (SELECT loanid FROM port.portmonth WHERE servicer='MRC');"
            ),
        },
        {
            "table": "port_basic_data_daily_loan_common_mrc",
            "source": "port.basic_data_daily_loan_common",
            "where": f"servicer='MRC' AND asofdate IN ('{remit_date}', '{pre_date}')",
            "sql": (
                "SELECT * FROM port.basic_data_daily_loan_common "
                f"WHERE servicer='MRC' AND asofdate IN ('{remit_date}', '{pre_date}');"
            ),
        },
        {
            "table": "port_basic_data_monthly_loan_common_mrc",
            "source": "port.basic_data_monthly_loan_common",
            "where": f"servicer='MRC' AND fctrdt='{fctrdt}'",
            "sql": (
                "SELECT * FROM port.basic_data_monthly_loan_common "
                f"WHERE servicer='MRC' AND fctrdt='{fctrdt}';"
            ),
        },
        {
            "table": "mrc_portmrcremitloanlevelrecap",
            "source": "mrc.portmrcremitloanlevelrecap",
            "where": f"fctrdt='{fctrdt}'",
            "sql": f"SELECT * FROM mrc.portmrcremitloanlevelrecap WHERE fctrdt='{fctrdt}';",
        },
        {
            "table": "mrc_portmrcremit3rdpartyadvances",
            "source": "mrc.portmrcremit3rdpartyadvances",
            "where": f"fctrdt IN ('{fctrdt}', '{fctrdt_1m}')",
            "sql": (
                "SELECT * FROM mrc.portmrcremit3rdpartyadvances "
                f"WHERE fctrdt IN ('{fctrdt}', '{fctrdt_1m}');"
            ),
        },
        {
            "table": "mrc_portmrcremitcorpadvances",
            "source": "mrc.portmrcremitcorpadvances",
            "where": f"fctrdt IN ('{fctrdt}', '{fctrdt_1m}')",
            "sql": (
                "SELECT * FROM mrc.portmrcremitcorpadvances "
                f"WHERE fctrdt IN ('{fctrdt}', '{fctrdt_1m}');"
            ),
        },
        {
            "table": "mrc_portmrcremitescrowadvances",
            "source": "mrc.portmrcremitescrowadvances",
            "where": f"fctrdt IN ('{fctrdt}', '{fctrdt_1m}')",
            "sql": (
                "SELECT * FROM mrc.portmrcremitescrowadvances "
                f"WHERE fctrdt IN ('{fctrdt}', '{fctrdt_1m}');"
            ),
        },
    ]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_mrc(remit_date: dt.date, out_dir: Path) -> Path:
    _bootstrap_prefect_env()
    # Imports must come AFTER bootstrap so PrefectFlow is on sys.path.
    from flow.remit_validation.mrc_db import MrcDB  # type: ignore[import-not-found]

    db = MrcDB(remit_date=remit_date, to_new_redshift=True, to_mysql=False)
    fctrdt = str(db.fctrdt)
    fctrdt_1m = str(db.fctrdt_1m)
    pre_date = str(db.pre_date)
    remit_str = str(remit_date)

    print(f"[snapshot_mrc] remit_date     = {remit_str}")
    print(f"[snapshot_mrc] pre_date       = {pre_date}")
    print(f"[snapshot_mrc] fctrdt (curr)  = {fctrdt}")
    print(f"[snapshot_mrc] fctrdt_1m      = {fctrdt_1m}")

    target = out_dir / "raw" / "mrc"
    target.mkdir(parents=True, exist_ok=True)
    manifest_entries = _build_mrc_manifest(fctrdt, fctrdt_1m, remit_str, pre_date)
    results: list[dict[str, object]] = []
    for entry in manifest_entries:
        table = entry["table"]
        sql = entry["sql"]
        print(f"[snapshot_mrc] -> {table}  ({entry['source']})")
        df = db.run_sql(sql)
        path = target / f"{table}.parquet"
        df.to_parquet(path, index=False)
        results.append({
            **entry,
            "rows": int(len(df)),
            "columns": list(map(str, df.columns)),
            "parquet": path.name,
            "sha256": _sha256(path),
        })
        print(f"     wrote {len(df):>7,} rows -> {path}")

    manifest = {
        "servicer": "MRC",
        "remit_date": remit_str,
        "pre_date": pre_date,
        "fctrdt": fctrdt,
        "fctrdt_1m": fctrdt_1m,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "tables": results,
    }
    manifest_path = target / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(f"[snapshot_mrc] manifest -> {manifest_path}")
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("remit_date", help="ISO date, e.g. 2026-04-30")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output root (default: <whitebox>/snapshots/<remit_date>/)")
    args = parser.parse_args(argv)
    remit_date = dt.date.fromisoformat(args.remit_date)
    out_dir = args.out or (WHITEBOX_ROOT / "snapshots" / args.remit_date)
    freeze_mrc(remit_date, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
