"""Snapshot freezer: pull Redshift tables into local Parquet files.

In Phase 1 this is a thin interface + JSON-driven fixture loader.
The real Redshift connection wiring is added in Phase 2 (mrc-snapshot)
once we point it at PrefectFlow's .env Vault token. For the infra
self-test, this script can populate snapshots/ from a JSON fixture so
the harness can be exercised end-to-end without a database.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def freeze_from_fixture(fixture_path: Path, out_dir: Path) -> list[Path]:
    """Read a JSON fixture {table_name: [rows]} and write one Parquet per table."""
    with fixture_path.open(encoding="utf-8") as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for table, rows in data.items():
        df = pd.DataFrame(rows)
        target = out_dir / f"{table}.parquet"
        df.to_parquet(target, index=False)
        written.append(target)
    return written


def freeze_from_redshift(servicer: str, remit_date: str, out_dir: Path) -> list[Path]:
    """Phase 2 hook: pull MRC/Carrington/etc tables for remit_date.

    Not implemented in Phase 1 — see mrc-snapshot todo. The real
    implementation will:
      1. Read $PREFECT_VAULT_TOKEN (or PrefectFlow/.env)
      2. Reuse PrefectFlow's db_cred path to get Redshift creds
      3. Enumerate the servicer's source tables (from validator YAMLs)
      4. SELECT each one filtered by remit_date when applicable
      5. Write Parquet under snapshots/<remit_date>/raw/<servicer>/
    """
    raise NotImplementedError(
        f"freeze_from_redshift({servicer!r}, {remit_date!r}, ...) "
        "is implemented in Phase 2 (mrc-snapshot todo)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fix = sub.add_parser("from-fixture", help="Phase 1: hydrate snapshot from JSON fixture")
    p_fix.add_argument("fixture", type=Path)
    p_fix.add_argument("out", type=Path)

    p_rs = sub.add_parser("from-redshift", help="Phase 2: pull from Redshift")
    p_rs.add_argument("servicer")
    p_rs.add_argument("remit_date")
    p_rs.add_argument("--out", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.cmd == "from-fixture":
        written = freeze_from_fixture(args.fixture, args.out)
        for p in written:
            print(p)
        return 0
    if args.cmd == "from-redshift":
        try:
            written = freeze_from_redshift(args.servicer, args.remit_date, args.out)
        except NotImplementedError as e:
            print(e, file=sys.stderr)
            return 2
        for p in written:
            print(p)
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
