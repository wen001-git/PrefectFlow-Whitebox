"""CLI entry point: ``python -m whitebox.engine ...``.

Runs the engine end-to-end against a chosen source, writes the
rendered XLSX, and persists ``RunResult.json`` next to it.

Example::

    python -m whitebox.engine \\
        --servicer MRC \\
        --remit-date 2026-04-30 \\
        --source cte-harness \\
        --output runs/p25-engine-smoke/

The ``--source`` flag accepts:

- ``cte-harness`` (default) — uses
  :class:`whitebox.engine.sources.CTEHarnessSource` pointed at the
  fixture dir given by ``--fixture-dir`` (defaults to
  ``tests/fixtures/cte_harness``).
- ``redshift`` — instantiates :class:`RedshiftSource`; will fail with
  :class:`EnvironmentNotConfigured` because the build is not wired to
  Redshift (G2a).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from whitebox.engine import (
    CTEHarnessSource,
    Engine,
    RedshiftSource,
    SourceConfig,
)
from whitebox.renderer import render_workbook, write_workbook


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m whitebox.engine",
        description=(
            "Run the Stage 2 P2.5 MRC validation engine end-to-end and "
            "persist its outputs (XLSX + RunResult.json)."
        ),
    )
    parser.add_argument("--servicer", required=True, help="Servicer id (e.g. MRC).")
    parser.add_argument(
        "--remit-date",
        required=True,
        help="Cycle date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--source",
        choices=("cte-harness", "redshift"),
        default="cte-harness",
        help="Source adapter to use. (default: cte-harness)",
    )
    parser.add_argument(
        "--fixture-dir",
        default=None,
        help=(
            "CTE harness fixture directory (only used with --source cte-harness). "
            "Defaults to <repo>/tests/fixtures/cte_harness."
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        help=(
            "Output directory. Files written: validation_report.xlsx, "
            "RunResult.json."
        ),
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help=(
            "Optional explicit run id. When omitted the engine derives a "
            "deterministic id from (servicer, remit_date, source)."
        ),
    )
    return parser.parse_args(argv)


def _build_source(args: argparse.Namespace) -> SourceConfig:
    if args.source == "cte-harness":
        if args.fixture_dir is not None:
            fixture_dir = Path(args.fixture_dir).resolve()
        else:
            fixture_dir = (
                Path(__file__).resolve().parents[2]
                / "tests"
                / "fixtures"
                / "cte_harness"
            )
        return CTEHarnessSource(fixture_dir=fixture_dir)
    if args.source == "redshift":
        return RedshiftSource()
    raise ValueError(f"unknown source kind: {args.source!r}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        remit_date = date.fromisoformat(args.remit_date)
    except ValueError as exc:
        sys.stderr.write(f"--remit-date must be YYYY-MM-DD: {exc}\n")
        return 2

    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = Engine.bootstrap_mrc()
    source = _build_source(args)

    try:
        result = engine.run(
            servicer=args.servicer,
            remit_date=remit_date,
            source=source,
            run_id=args.run_id,
        )
    except Exception as exc:  # noqa: BLE001 — CLI surface: report & exit non-zero
        sys.stderr.write(f"engine error: {type(exc).__name__}: {exc}\n")
        return 1

    xlsx_path = output_dir / "validation_report.xlsx"
    wb = render_workbook(result.sheet_models)
    write_workbook(wb, xlsx_path)

    json_path = output_dir / "RunResult.json"
    payload = result.to_dict()
    payload["written_at"] = datetime.now(tz=timezone.utc).isoformat()
    payload["xlsx_path"] = str(xlsx_path)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    sys.stdout.write(
        f"engine run complete: {result.run_id} "
        f"verdict={result.overall_verdict.value} "
        f"sheets={len(result.sheets)} "
        f"xlsx={xlsx_path}\n"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry point
    raise SystemExit(main())
