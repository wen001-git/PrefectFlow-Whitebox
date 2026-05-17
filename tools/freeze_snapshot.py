"""tools/freeze_snapshot.py — G2a snapshot freezer (binding).

Freeze the exact MRC validator input dataset to local files so Stage 2
development is decoupled from live Redshift. See session plan.md section 4.2
for the binding spec and `decisions.md` 2026-05-17 entry "G2 redefinition".

This tool has two subcommands:

  plan   — static-extract SQL literals from legacy `flow/remit_validation/
           {servicer}_db.py` and `{servicer}_validation.py`, write one
           `.sql` file per query + a `_plan_index.json` review file.
           **No Redshift access required.** Agent-safe.

  export — execute the reviewed plan against Redshift, write Parquet
           files and update `_manifest.json`. **Requires Redshift VPN +
           credentials.** Operator step (user or colleague). Currently
           a NotImplementedError stub — implement in the operator's
           environment so credentials never enter this repo.

Folder layout produced under `<out>`:

    <out>/
      _export_queries/<logical_name>.sql       (plan + export)
      _plan_index.json                         (plan)
      _manifest.json                           (export)
      parquet/<logical_name>.parquet           (export)
      csv/<logical_name>.csv (optional)        (export, --also-csv)

Manifest entry schema is encoded in MANIFEST_ENTRY_TEMPLATE below and is
the single source of truth — any change must propagate to
`docs/mrc/1.6-baseline.{zh,en}.md` section 9 and to the G2b adapter
`tools/legacy_adapter.py` when that lands.

The Phase 1 fixture-loader skeleton has been renamed to
`tools/_freeze_snapshot_phase1.py` and is retained for the JSON-fixture
self-test only.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

MANIFEST_VERSION = "1.0"

MANIFEST_ENTRY_TEMPLATE: dict[str, Any] = {
    "logical_name": "",
    "source": {"type": "redshift", "schema": "", "table": ""},
    "export_sql_path": "",
    "filter": {},
    "exported_at": None,
    "exporter": None,
    "format": "parquet",
    "path": "",
    "row_count": None,
    "column_count": None,
    "columns": [],
    "sha256_file": None,
    "sha256_canonical_rows": None,
    "redshift_session": {"user": None, "cluster": None, "query_id": None},
}


@dataclass
class ExportPlanEntry:
    logical_name: str
    source_module: str
    source_function: str
    sql: str
    filter_hints: dict[str, str] = field(default_factory=dict)
    notes: str = ""


def _is_sql_string(s: str) -> bool:
    head = s.lstrip().lower()
    return head.startswith(("select ", "with ", "select\n", "with\n"))


def extract_sql_literals(py_path: Path) -> list[tuple[str, str]]:
    """Return [(enclosing_function_name, sql_text)] for every SQL-shaped
    string literal in `py_path`. Handles plain strings and f-strings;
    f-string placeholders are rendered as ``{<expr>}`` so reviewers see them.
    """
    source = py_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_path))
    out: list[tuple[str, str]] = []

    def stringify(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(v.value)
                elif isinstance(v, ast.FormattedValue):
                    try:
                        expr = ast.unparse(v.value)
                    except Exception:
                        expr = "?"
                    parts.append("{" + expr + "}")
            return "".join(parts)
        return None

    def walk(node: ast.AST, enclosing: str = "<module>") -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            enclosing = node.name
        for child in ast.iter_child_nodes(node):
            s = stringify(child)
            if s is not None and _is_sql_string(s):
                out.append((enclosing, s))
            else:
                walk(child, enclosing)

    walk(tree)
    return out


def build_export_plan(legacy_root: Path, servicer: str) -> list[ExportPlanEntry]:
    base = legacy_root / "flow" / "remit_validation"
    candidates = [base / f"{servicer}_db.py", base / f"{servicer}_validation.py"]
    plan: list[ExportPlanEntry] = []
    seen: set[str] = set()
    for f in candidates:
        if not f.exists():
            continue
        for func, sql in extract_sql_literals(f):
            sig = hashlib.sha1(sql.encode("utf-8")).hexdigest()[:12]
            if sig in seen:
                continue
            seen.add(sig)
            hints = {ph: "<resolve before export>" for ph in re.findall(r"\{([^{}]+)\}", sql)}
            plan.append(
                ExportPlanEntry(
                    logical_name=f"{servicer}_{f.stem}_{func}_{sig}",
                    source_module=str(f.relative_to(legacy_root)),
                    source_function=func,
                    sql=sql.strip(),
                    filter_hints=hints,
                    notes="auto-extracted; resolve `{...}` placeholders before export",
                )
            )
    return plan


def cmd_plan(args: argparse.Namespace) -> int:
    legacy_root = Path(args.legacy_root).resolve()
    out_dir = Path(args.out).resolve()
    queries_dir = out_dir / "_export_queries"
    queries_dir.mkdir(parents=True, exist_ok=True)
    plan = build_export_plan(legacy_root, args.servicer)
    if not plan:
        print(
            f"[ERR] no SQL extracted from {legacy_root}/flow/remit_validation/"
            f"{args.servicer}_*.py",
            file=sys.stderr,
        )
        return 2
    for entry in plan:
        sql_file = queries_dir / f"{entry.logical_name}.sql"
        header = (
            f"-- auto-extracted by tools/freeze_snapshot.py plan\n"
            f"-- source: {entry.source_module} :: {entry.source_function}\n"
            f"-- servicer: {args.servicer}\n"
            f"-- remit_date: {args.remit_date}\n"
            f"-- placeholders to resolve: "
            f"{', '.join(entry.filter_hints) if entry.filter_hints else '(none)'}\n"
            f"-- notes: {entry.notes}\n\n"
        )
        sql_file.write_text(header + entry.sql + "\n", encoding="utf-8")
    plan_index = out_dir / "_plan_index.json"
    plan_index.write_text(
        json.dumps(
            {
                "manifest_version": MANIFEST_VERSION,
                "servicer": args.servicer,
                "remit_date": args.remit_date,
                "legacy_root": str(legacy_root),
                "entries": [asdict(e) for e in plan],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"[OK] wrote {len(plan)} SQL files + _plan_index.json under {out_dir}")
    print("[NEXT] 1) review each `_export_queries/*.sql` and resolve placeholders.")
    print("       2) run `freeze_snapshot.py export` from a host with Redshift access.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    out_dir = Path(args.out).resolve()
    queries_dir = out_dir / "_export_queries"
    if not queries_dir.exists():
        print(f"[ERR] {queries_dir} not found - run `plan` first.", file=sys.stderr)
        return 2
    if not args.redshift_conn:
        print("[ERR] --redshift-conn (or REDSHIFT_URL env) required", file=sys.stderr)
        return 2
    raise NotImplementedError(
        "G2a export step is an operator action - implement in the operator's "
        "environment so Redshift credentials never enter this repo. "
        "Required behavior per session plan.md section 4.2: for each "
        "_export_queries/<name>.sql, execute against Redshift, write "
        "parquet/<name>.parquet, compute sha256_file + sha256_canonical_rows "
        "(over rows sorted by primary key), and upsert the entry into "
        "_manifest.json using MANIFEST_ENTRY_TEMPLATE."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="G2a snapshot freezer - see module docstring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="static-extract SQL from legacy code (no Redshift)")
    p_plan.add_argument("servicer", choices=["mrc"])
    p_plan.add_argument("remit_date")
    p_plan.add_argument("--legacy-root", required=True)
    p_plan.add_argument("--out", required=True)
    p_plan.set_defaults(func=cmd_plan)

    p_exp = sub.add_parser("export", help="execute the plan against Redshift (operator step)")
    p_exp.add_argument("servicer", choices=["mrc"])
    p_exp.add_argument("remit_date")
    p_exp.add_argument("--legacy-root", required=True)
    p_exp.add_argument("--out", required=True)
    p_exp.add_argument("--redshift-conn", default=os.environ.get("REDSHIFT_URL"))
    p_exp.add_argument("--also-csv", action="store_true")
    p_exp.set_defaults(func=cmd_export)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
