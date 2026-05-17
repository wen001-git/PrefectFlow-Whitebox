"""Column-level lineage builder.

For each validator with a SQL file, uses sqlglot to derive
`output_column <- f(input_table.input_column, ...)` and writes the
results into the matching sheets/<sheet>.yaml `columns.<col>.sources`
field. Also emits a Mermaid DAG of dataset-level lineage to
docs/lineage.{en,zh}.md (via autodoc).

This script is intentionally idempotent: re-running on already-filled
YAMLs replaces only the `sources` and `expression` fields (which are
declared auto-managed); human-edited fields (rule_*, sample_values, type,
format, business_impact_*) are preserved.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import sqlglot
import yaml
from sqlglot import exp
from sqlglot.lineage import lineage as sg_lineage
from sqlglot.optimizer.qualify import qualify

from tools.registry import Registry, load_all

# Tell yaml to emit nicer flow-style for short sequences
yaml.SafeDumper.add_representer(
    list,
    lambda dumper, data: dumper.represent_sequence(
        "tag:yaml.org,2002:seq", data, flow_style=len(data) <= 2 and all(not isinstance(x, dict) for x in data)
    ),
)

DIALECT = "redshift"


def _final_select(parsed: exp.Expression) -> exp.Select | None:
    """Return the outermost SELECT expression (the one whose columns become
    the validator's output columns)."""
    if isinstance(parsed, exp.Select):
        return parsed
    # Some queries wrap in CTEs / unions; find the final projection.
    for node in parsed.walk():
        if isinstance(node, exp.Select):
            return node
    return None


def _output_columns(select: exp.Select) -> list[str]:
    cols: list[str] = []
    for proj in select.expressions:
        alias = proj.alias_or_name
        if alias:
            cols.append(alias)
    return cols


def _extract_sources_for_column(
    parsed: exp.Expression, sql: str, output_col: str
) -> tuple[list[dict[str, str | None]], str | None]:
    """Return (sources, expression) for the given output column."""
    try:
        node = sg_lineage(output_col, sql, dialect=DIALECT)
    except Exception:
        # sqlglot may fail on complex queries; fall back to a naive scan.
        return _naive_sources(parsed, output_col), None

    sources: list[dict[str, str | None]] = []
    expression: str | None = node.expression.sql(dialect=DIALECT) if node.expression else None
    seen: set[tuple[str, str]] = set()

    def _walk(n: Any) -> None:
        for child in n.downstream:
            # Leaf nodes have no further downstream and reference base table cols.
            if not child.downstream:
                col = child.name
                if "." in col:
                    table, colname = col.rsplit(".", 1)
                else:
                    table, colname = "", col
                key = (table, colname)
                if key not in seen:
                    seen.add(key)
                    sources.append({"table": table, "column": colname, "transform": None})
            else:
                _walk(child)

    _walk(node)
    return sources, expression


def _naive_sources(
    parsed: exp.Expression, output_col: str
) -> list[dict[str, str | None]]:
    """Fallback: collect every Column ref in the validator that mentions
    output_col by alias."""
    sources: list[dict[str, str | None]] = []
    seen: set[tuple[str, str]] = set()
    for col in parsed.find_all(exp.Column):
        table = col.table or ""
        name = col.name
        key = (table, name)
        if key not in seen:
            seen.add(key)
            sources.append({"table": table, "column": name, "transform": None})
    return sources


def _qualify_sql(sql: str) -> exp.Expression:
    parsed = sqlglot.parse_one(sql, dialect=DIALECT)
    try:
        return qualify(parsed, dialect=DIALECT)  # type: ignore[return-value]
    except Exception:
        return parsed  # type: ignore[return-value]


def build_for_validator(reg: Registry, vid: str) -> list[str]:
    """Back-fill sources/expression for one validator into its sheets."""
    v = reg.validators[vid]
    if not v.sql:
        return []
    parsed = _qualify_sql(v.sql)
    select = _final_select(parsed)
    if select is None:
        return [f"{v.path}: could not find a final SELECT in SQL"]
    out_cols = _output_columns(select)

    messages: list[str] = []
    for sheet_name in v.data.get("related_sheets", []):
        sheet = reg.sheets.get(sheet_name)
        if sheet is None:
            messages.append(f"{v.path}: related_sheets references unknown sheet '{sheet_name}'")
            continue
        changed = False
        for col_name, col_meta in sheet.columns.items():
            if col_name not in out_cols:
                continue
            sources, expression = _extract_sources_for_column(parsed, v.sql, col_name)
            col_meta["sources"] = sources
            if expression is not None:
                col_meta["expression"] = expression
            col_meta.setdefault("related_validator", vid)
            changed = True
        if changed:
            _write_sheet_yaml(sheet.path, sheet.data)
            messages.append(f"updated {sheet.path}")
    return messages


def _write_sheet_yaml(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )


def main() -> int:
    reg = load_all()
    if reg.errors:
        for e in reg.errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    any_msg = False
    for vid in reg.validators:
        for msg in build_for_validator(reg, vid):
            print(msg)
            any_msg = True
    if not any_msg:
        print("No updates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
