"""tools/freeze_snapshot.py — G2a snapshot freezer (binding).

Freeze the exact MRC validator input dataset to local files so Stage 2
development is decoupled from live Redshift. See session plan.md section 4.2
for the binding spec and `decisions.md` 2026-05-17 entry "G2 redefinition".

This tool has three subcommands:

  plan   — static-extract SQL literals from legacy `flow/remit_validation/
           {servicer}_db.py` and `{servicer}_validation.py`, write one
           `.sql` file per query + a `_plan_index.json` review file +
           a `_coverage.md` human-readable table.
           Follows import edges recursively (bounded at flow/ modules) to
           catch SQL templates defined in transitively-imported files.
           **No Redshift access required.** Agent-safe.

  export — execute the reviewed plan against Redshift, write Parquet
           files and update `_manifest.json`. **Requires Redshift VPN +
           credentials.** Operator step (user or colleague). Currently
           a NotImplementedError stub — implement in the operator's
           environment so credentials never enter this repo.

  verify — validate a populated input_snapshots/ folder.  Checks
           coverage parity, manifest schema, file/checksum integrity,
           SQL hash binding, schema sanity, and fan-out consistency.
           **No Redshift access required.**  Exits 0 on full pass,
           1 on any core failure, 2 on strict-only failure.

Folder layout produced under `<out>`:

    <out>/
      _export_queries/
        template/<logical_name>.sql            (plan + export)
        resolved/<logical_name>.sql            (plan --resolve, single-binding)
        resolved/<logical_name>__<k>=<v>.sql   (plan --resolve, fan-out variant)
        _coverage.md                           (plan, human-readable table)
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

v2.0 (G2a A1): exhaustive SQL coverage scan — recursive import walker,
8-pattern detection, _coverage.md output, --min-expected gate.
v2.1 (G2a A3): --resolve flag; template/ + resolved/ split; _bindings.json.
v2.2 (G2a A4): verify subcommand; C1–C8 checks; _verify_report.json.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_VERSION = "1.0"
TOOL_VERSION = "2.2"

# Known placeholder → human-readable resolution hint
_PLACEHOLDER_HINTS: dict[str, str] = {
    "mrc_db.fctrdt": "factor-date (YYYY-MM-01) for remit cycle, e.g. '2026-05-01'",
    "mrc_db.fctrdt_1m": "prior-month factor-date (YYYY-MM-01), e.g. '2026-04-01'",
    "fctrdt": "factor-date parameter (YYYY-MM-01), e.g. '2026-05-01'",
    "input_fctrdt": "factor-date literal placeholder replaced via .replace(), e.g. '2026-05-01'",
    "input_curr_month_end": "remit month-end placeholder replaced via .replace(), e.g. '2026-04-30'",
    "input_pre_month_end": "prior month-end placeholder replaced via .replace(), e.g. '2026-03-31'",
    "service": "servicer name string, e.g. 'MRC'",
    "table": "Redshift table name resolved at runtime",
    "query_date": "as-of date for daily snapshot",
    "str(query_date)": "as-of date for daily snapshot (string form)",
    "str(self.fctrdt)": "factor-date for this cycle (string form)",
    "str(self.remit_date)": "remit date for this cycle (string form)",
    "str(self.pre_date)": "prior month-end date (string form)",
}

# Built-in MRC 2026-04-30 anchor bindings (used when --resolve without --bindings file)
_MRC_BUILTIN_BINDINGS: dict[str, str] = {
    "mrc_db.fctrdt": "2026-05-01",
    "mrc_db.fctrdt_1m": "2026-04-01",
    "fctrdt": "2026-05-01",
    "service": "MRC",
    "servicer": "MRC",
    "remit_date": "2026-04-30",
    "input_fctrdt": "2026-05-01",
    "input_curr_month_end": "2026-04-30",
    "input_pre_month_end": "2026-03-31",
}

# Built-in fan-out: templates that must be emitted once per binding set
_MRC_BUILTIN_FANOUT: dict[str, list[dict[str, str]]] = {
    "_mrc_adv_info_sql": [
        {"fctrdt": "2026-05-01"},
        {"fctrdt": "2026-04-01"},
    ],
}


def load_bindings(bindings_path: Path | None) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    """Load bindings from a JSON file, or return the built-in MRC defaults."""
    if bindings_path is None:
        return _MRC_BUILTIN_BINDINGS, _MRC_BUILTIN_FANOUT
    data = json.loads(bindings_path.read_text(encoding="utf-8"))
    bindings = data.get("bindings", {})
    fanout = data.get("fanout", {})
    return bindings, fanout


def _apply_bindings(
    sql: str, bindings: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Apply all bindings to a SQL template.

    Handles both:
    - f-string style: ``{mrc_db.fctrdt}`` → ``2026-05-01``
    - .replace() style: bare string ``input_fctrdt`` → ``2026-05-01``
      (these appear as ``'input_fctrdt'`` inside the SQL value literals)

    Returns (resolved_sql, bindings_used).
    """
    result = sql
    used: dict[str, str] = {}

    for key in sorted(bindings, key=len, reverse=True):
        value = bindings[key]
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, value)
            used[key] = value

    for key in sorted(bindings, key=len, reverse=True):
        value = bindings[key]
        if key.startswith("input_") and key in result:
            result = result.replace(key, value)
            used[key] = value

    return result, used


def _unresolved_placeholders(sql: str) -> list[str]:
    """Return any remaining ``{...}`` placeholders in *sql* after resolution."""
    return re.findall(r"\{([^{}]+)\}", sql)


def resolve_template(
    owner: str,
    sql_template: str,
    bindings: dict[str, str],
    fanout: dict[str, list[dict[str, str]]],
) -> list[tuple[str, str, dict[str, str]]]:
    """Resolve a SQL template to one or more (suffix, resolved_sql, bindings_used) tuples.

    If *owner* is in *fanout*, produces one tuple per fanout binding set.
    Otherwise produces a single tuple with suffix="".

    Raises ``ValueError`` if any placeholder remains unresolved after all bindings.
    """
    fanout_sets = fanout.get(owner)
    if fanout_sets is None:
        resolved, used = _apply_bindings(sql_template, bindings)
        remaining = _unresolved_placeholders(resolved)
        if remaining:
            raise ValueError(
                f"Unresolved placeholder(s) in '{owner}': {remaining}"
            )
        return [("", resolved, used)]

    results: list[tuple[str, str, dict[str, str]]] = []
    for override in fanout_sets:
        effective = dict(bindings)
        effective.update(override)
        resolved, used = _apply_bindings(sql_template, effective)
        remaining = _unresolved_placeholders(resolved)
        if remaining:
            raise ValueError(
                f"Unresolved placeholder(s) in '{owner}' (fanout {override}): {remaining}"
            )
        suffix = "__" + "_".join(f"{k}={v}" for k, v in override.items())
        results.append((suffix, resolved, used))
    return results


# Chapter 1.2 catalog: MRC SQL templates explicitly documented
_CHAPTER_12_CATALOG: dict[str, str] = {
    "mrc_summary_check": "V1 — aggregate sums from port.portmonth (fctrdt filter)",
    "mrc_adv_validation": "V2 — 3-CTE advance balance comparison (50 lines)",
    "mrc_general_check": "V3 — 3-CTE general info comparison (71 lines)",
    "mrc_service_fee_check": "V4 — 3-way join on portmrcremitloanlevelrecap",
    "_mrc_adv_info_sql": "V5 — 3-way UNION ALL for advance info detail",
}


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


@dataclass
class SqlHit:
    """Rich SQL hit with full metadata for coverage reporting."""

    file_rel: str  # relative to legacy_root, forward slashes
    start_line: int
    end_line: int
    owner: str  # function name, variable name, or "<module>"
    owner_type: str  # "function" | "variable" | "module"
    sql_template: str  # verbatim SQL with {placeholder} preserved
    pattern_type: str  # "f-string" | "f-string-noexpr" | "str-literal"
    placeholders: dict[str, str]  # {name: resolution_hint}
    mrc_relevant: bool
    proposed_frozen_as: str  # path under baselines/.../parquet/ or "n/a"
    notes: str
    sha: str  # sha1[:12] of sql_template for deduplication


# ---------------------------------------------------------------------------
# Core SQL-string helpers
# ---------------------------------------------------------------------------


def _is_sql_string(s: str) -> bool:
    head = s.lstrip().lower()
    return head.startswith(
        ("select ", "select\n", "with ", "with\n",
         "insert ", "insert\n", "update ", "update\n",
         "delete ", "delete\n", "create ", "create\n")
    )


def _stringify_node(node: ast.AST) -> str | None:
    """Convert a Constant or JoinedStr AST node to its string value.

    f-string placeholders are rendered as ``{<expr>}`` so reviewers see them.
    Returns None for non-string nodes.
    """
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


def _pattern_type(node: ast.AST) -> str:
    if isinstance(node, ast.JoinedStr):
        has_expr = any(isinstance(v, ast.FormattedValue) for v in node.values)
        return "f-string" if has_expr else "f-string-noexpr"
    return "str-literal"


def _node_end_line(node: ast.AST, fallback: int = 0) -> int:
    return int(getattr(node, "end_lineno", None) or fallback)


# ---------------------------------------------------------------------------
# Legacy API — kept for backward compatibility
# ---------------------------------------------------------------------------


def extract_sql_literals(py_path: Path) -> list[tuple[str, str]]:
    """Return [(enclosing_function_name, sql_text)] for every SQL-shaped
    string literal in ``py_path``.  Handles plain strings and f-strings;
    f-string placeholders are rendered as ``{<expr>}`` so reviewers see them.
    """
    source = py_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_path))
    out: list[tuple[str, str]] = []

    def walk(node: ast.AST, enclosing: str = "<module>") -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            enclosing = node.name
        for child in ast.iter_child_nodes(node):
            s = _stringify_node(child)
            if s is not None and _is_sql_string(s):
                out.append((enclosing, s))
            else:
                walk(child, enclosing)

    walk(tree)
    return out


# ---------------------------------------------------------------------------
# Enhanced scanner: recursive import walker + rich SqlHit extraction
# ---------------------------------------------------------------------------


def _collect_flow_imports(root: Path, start_files: list[Path]) -> list[Path]:
    """Walk Python imports recursively, bounded at ``flow/`` modules.

    Returns an ordered list of unique Python files (start_files first,
    then transitively-imported flow/ modules in BFS order).
    """
    visited: list[Path] = []
    seen: set[str] = set()
    queue = list(start_files)

    while queue:
        f = queue.pop(0)
        key = str(f.resolve())
        if key in seen:
            continue
        seen.add(key)
        if not f.exists():
            continue
        visited.append(f)

        try:
            source = f.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(f))
        except Exception:
            continue

        for node in ast.walk(tree):
            module_name: str | None = None
            if isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("flow.") or alias.name == "flow":
                        candidate = root / (alias.name.replace(".", "/") + ".py")
                        if str(candidate.resolve()) not in seen and candidate.exists():
                            queue.append(candidate)
                continue

            if module_name and (
                module_name.startswith("flow.") or module_name == "flow"
            ):
                candidate = root / (module_name.replace(".", "/") + ".py")
                if str(candidate.resolve()) not in seen and candidate.exists():
                    queue.append(candidate)

    return visited


def _is_mrc_relevant(sql: str, file_rel: str, owner: str) -> bool:
    """Heuristic: is this SQL string relevant to the MRC validator flow?"""
    sql_l = sql.lower()
    owner_l = owner.lower()

    if "mrc_validation" in file_rel:
        return True
    if "mrc" in owner_l:
        return True
    if "'mrc'" in sql_l:
        return True
    # ValidationBaseDB helpers inherited by MrcDB (carrington_db.py)
    if "carrington_db" in file_rel and owner in (
        "get_port_month_data",
        "get_port_funding_data",
    ):
        return True
    return False


def _resolve_placeholder_hints(raw_phs: list[str]) -> dict[str, str]:
    return {
        ph: _PLACEHOLDER_HINTS.get(ph, "<resolve before export>")
        for ph in raw_phs
    }


def _proposed_frozen_as(
    owner: str, mrc_relevant: bool, servicer: str, remit_date: str
) -> str:
    if not mrc_relevant:
        return "n/a (non-MRC SQL — not frozen for this servicer snapshot)"
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", owner).strip("_")
    return (
        f"baselines/{servicer}/{remit_date}/input_snapshots/parquet/{clean}.parquet"
    )


def extract_sql_hits(
    py_path: Path,
    legacy_root: Path,
    servicer: str = "mrc",
    remit_date: str = "2026-04-30",
) -> list[SqlHit]:
    """Extract all SQL strings from *py_path* with rich metadata.

    Handles:
    - Bare string literals (SQL keywords at start)
    - f-strings with ``{expr}`` placeholders
    - Module-level variable assignments (captures variable name as owner)
    - SQL inside function bodies (captures function name as owner)
    - SQL passed as call arguments (e.g. cursor.execute, read_sql)
    """
    try:
        source = py_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_path))
    except Exception:
        return []

    file_rel = str(py_path.relative_to(legacy_root)).replace("\\", "/")
    raw: list[tuple[str, str, int, int, str, str]] = []
    # (owner, owner_type, start_line, end_line, sql, pattern_type)

    def walk(node: ast.AST, fn_ctx: str | None, var_ctx: str | None) -> None:  # noqa: C901
        # ---- function/method definition: descend with function name as context
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.iter_child_nodes(node):
                walk(child, node.name, None)
            return

        # ---- assignment: capture variable name from target
        if isinstance(node, ast.Assign):
            vname: str | None = None
            if node.targets and isinstance(node.targets[0], ast.Name):
                vname = node.targets[0].id
            # Walk the RHS value with var_ctx = vname
            walk(node.value, fn_ctx, vname)
            # Walk targets (no SQL expected there)
            for t in node.targets:
                walk(t, fn_ctx, None)
            return

        # ---- annotated assignment
        if isinstance(node, ast.AnnAssign):
            vname2: str | None = (
                node.target.id
                if isinstance(node.target, ast.Name)
                else None
            )
            if node.value is not None:
                walk(node.value, fn_ctx, vname2)
            walk(node.target, fn_ctx, None)
            return

        # ---- check if this node is directly a SQL string
        s = _stringify_node(node)
        if s is not None and _is_sql_string(s):
            # Determine owner
            if var_ctx is not None and fn_ctx is None:
                # Module-level variable assignment
                owner = var_ctx
                otype = "variable"
            elif fn_ctx is not None:
                owner = fn_ctx
                otype = "function"
            elif var_ctx is not None:
                owner = var_ctx
                otype = "variable"
            else:
                owner = "<module>"
                otype = "module"

            sl = int(getattr(node, "lineno", 0))
            el = _node_end_line(node, sl)
            pat = _pattern_type(node)
            raw.append((owner, otype, sl, el, s, pat))
            return  # don't recurse into the string itself

        # ---- default: recurse into children, resetting var_ctx
        for child in ast.iter_child_nodes(node):
            walk(child, fn_ctx, None)

    for top_node in ast.iter_child_nodes(tree):
        walk(top_node, None, None)

    # Deduplicate by SHA1 and build SqlHit objects
    seen_sha: set[str] = set()
    hits: list[SqlHit] = []
    for owner, otype, sl, el, sql, pat in raw:
        sha = hashlib.sha1(sql.encode("utf-8")).hexdigest()[:12]
        if sha in seen_sha:
            continue
        seen_sha.add(sha)

        raw_phs = re.findall(r"\{([^{}]+)\}", sql)
        placeholders = _resolve_placeholder_hints(raw_phs)
        mrc_rel = _is_mrc_relevant(sql, file_rel, owner)
        proposed = _proposed_frozen_as(owner, mrc_rel, servicer, remit_date)

        notes_parts: list[str] = []
        if not mrc_rel:
            notes_parts.append("non-MRC (other servicer SQL in shared module)")
        if raw_phs:
            notes_parts.append(
                f"resolve {len(raw_phs)} placeholder(s) before export"
            )
        if otype == "variable":
            notes_parts.append(
                "module-level template (used via .replace() in caller)"
            )
        notes = "; ".join(notes_parts) if notes_parts else "auto-extracted"

        hits.append(
            SqlHit(
                file_rel=file_rel,
                start_line=sl,
                end_line=el,
                owner=owner,
                owner_type=otype,
                sql_template=sql.strip(),
                pattern_type=pat,
                placeholders=placeholders,
                mrc_relevant=mrc_rel,
                proposed_frozen_as=proposed,
                notes=notes,
                sha=sha,
            )
        )

    return hits


# ---------------------------------------------------------------------------
# Coverage markdown generator
# ---------------------------------------------------------------------------


def _get_source_sha(legacy_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(legacy_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "(unavailable)"


def build_coverage_md(
    hits: list[SqlHit],
    scan_files: list[Path],
    legacy_root: Path,
    servicer: str,
    remit_date: str,
    scan_ts: str,
    resolve_enabled: bool = False,
    bindings: dict[str, str] | None = None,
    fanout: dict[str, list[dict[str, str]]] | None = None,
    resolved_count: int = 0,
) -> str:
    """Build the human-readable ``_coverage.md`` content."""
    source_sha = _get_source_sha(legacy_root)
    total = len(hits)
    mrc_count = sum(1 for h in hits if h.mrc_relevant)
    n_files = len(scan_files)

    lines: list[str] = []
    lines.append("# MRC SQL Coverage Report\n")
    lines.append(
        f"_Generated by `tools/freeze_snapshot.py plan` (v{TOOL_VERSION}) "
        f"on {scan_ts}_\n"
    )

    lines.append("\n## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total SQL strings found | **{total}** |")
    lines.append(f"| MRC-relevant SQL strings | **{mrc_count}** |")
    lines.append(f"| Source files scanned | {n_files} |")
    lines.append(f"| Servicer | {servicer} |")
    lines.append(f"| Remit date | {remit_date} |")
    lines.append(f"| Source repo SHA | `{source_sha}` |")
    lines.append(f"| Scan timestamp | {scan_ts} |")
    lines.append(f"| Tool version | {TOOL_VERSION} |")

    # Group hits by file
    from collections import defaultdict
    by_file: dict[str, list[SqlHit]] = defaultdict(list)
    for h in hits:
        by_file[h.file_rel].append(h)

    lines.append("\n## SQL strings by source file\n")
    for file_rel, file_hits in sorted(by_file.items()):
        lines.append(f"### `{file_rel}`\n")
        lines.append(
            "| lines | owner | owner-type | pattern | MRC? | proposed-frozen-as "
            "| placeholders | notes |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        for h in file_hits:
            line_range = (
                f"{h.start_line}–{h.end_line}"
                if h.end_line != h.start_line
                else str(h.start_line)
            )
            frozen = (
                f"`{h.proposed_frozen_as}`"
                if not h.proposed_frozen_as.startswith("n/a")
                else h.proposed_frozen_as
            )
            ph_count = len(h.placeholders)
            ph_str = (
                ", ".join(f"`{k}`" for k in h.placeholders)
                if ph_count
                else "(none)"
            )
            mrc_flag = "✅" if h.mrc_relevant else "—"
            notes_safe = h.notes.replace("|", "\\|")
            lines.append(
                f"| {line_range} | `{h.owner}` | {h.owner_type} | {h.pattern_type} "
                f"| {mrc_flag} | {frozen} | {ph_str} | {notes_safe} |"
            )
        lines.append("")

    # Coverage delta vs chapter 1.2 catalog
    lines.append("\n## Coverage delta vs chapter 1.2 catalog\n")
    lines.append(
        "Chapter `1.2 1.2-dataflow (1.2-dataflow.zh.md)` catalogs the following "
        "MRC SQL templates:\n"
    )
    all_owners = {h.owner for h in hits}
    missing: list[str] = []
    for key, desc in _CHAPTER_12_CATALOG.items():
        found_hits = [h for h in hits if h.owner == key]
        if found_hits:
            fh = found_hits[0]
            lines.append(
                f"- **`{key}`** ({desc}) — "
                f"✅ found in `{fh.file_rel}` lines {fh.start_line}–{fh.end_line}"
            )
        else:
            lines.append(
                f"- **`{key}`** ({desc}) — "
                f"❌ **MISSING** — not detected by current scanner (A2 target)"
            )
            missing.append(key)

    if not missing:
        lines.append(
            "\n> ✅ **All 5 chapter-1.2 templates are covered by the enhanced scanner.** "
            "No A2 targets."
        )
    else:
        lines.append(
            f"\n> ⚠️ **{len(missing)} template(s) still missing** "
            f"— deferred to A2: {', '.join(f'`{m}`' for m in missing)}"
        )

    # Scanned files list
    lines.append("\n## Files scanned (import walk)\n")
    for f in scan_files:
        try:
            rel = str(f.relative_to(legacy_root)).replace("\\", "/")
        except ValueError:
            rel = str(f)
        lines.append(f"- `{rel}`")

    # How to read this file
    lines.append("\n---\n")
    lines.append("## How to read this file\n")
    lines.append(
        "- **lines**: source line range in the original PrefectFlow repo file.\n"
        "- **owner**: the Python function or module-level variable that holds the SQL.\n"
        "- **owner-type**: `function` = SQL inside a def; `variable` = module-level template.\n"
        "- **pattern**: `f-string` = Python f-string with `{expr}` substitution; "
        "`f-string-noexpr` = f-string syntax but no Python expressions "
        "(placeholders are bare strings replaced via `.replace()`); "
        "`str-literal` = plain string constant.\n"
        "- **MRC?**: ✅ means this SQL is executed in the MRC validation flow; "
        "— means it lives in a shared/other-servicer module.\n"
        "- **proposed-frozen-as**: suggested Parquet filename under "
        "`baselines/mrc/{remit_date}/input_snapshots/parquet/` "
        "once the operator runs `freeze_snapshot.py export`.\n"
        "- **placeholders**: Python `{expr}` expressions or bare-string placeholders "
        "that must be resolved before executing the SQL against Redshift.\n"
        "- To execute a plan: resolve all placeholders, then run "
        "`freeze_snapshot.py export` from a host with Redshift VPN + credentials.\n"
    )

    if resolve_enabled and bindings:
        lines.append("\n## Bindings used for --resolve\n")
        lines.append("| Placeholder | Resolved value |")
        lines.append("|---|---|")
        for k, v in sorted(bindings.items()):
            lines.append(f"| `{k}` | `{v}` |")
        if fanout:
            lines.append("\n### Fan-out templates\n")
            for owner, sets in fanout.items():
                lines.append(f"- **`{owner}`** → {len(sets)} resolved variants:")
                for s in sets:
                    desc = ", ".join(f"`{k}={v}`" for k, v in s.items())
                    lines.append(f"  - {desc}")
        lines.append(f"\n_Resolved SQL files: **{resolved_count}** (template count: {sum(1 for h in hits if h.mrc_relevant)})_\n")
        lines.append("\n## Template / Resolved split\n")
        lines.append(
            "- `_export_queries/template/` — verbatim templates (all 21 SQL strings, {placeholder} preserved)\n"
            "- `_export_queries/resolved/` — placeholders bound to anchor values; "
            "multi-binding templates (e.g. `_mrc_adv_info_sql`) emit one file per binding set\n"
        )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Enhanced plan builder
# ---------------------------------------------------------------------------


def build_export_plan(legacy_root: Path, servicer: str) -> list[ExportPlanEntry]:
    """Legacy plan builder — scans only {servicer}_db.py + {servicer}_validation.py."""
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


def build_export_plan_enhanced(
    legacy_root: Path,
    servicer: str,
    remit_date: str,
) -> tuple[list[SqlHit], list[Path]]:
    """Enhanced plan builder — walks import graph from {servicer}_validation.py."""
    base = legacy_root / "flow" / "remit_validation"
    entry_files = [
        f
        for f in [base / f"{servicer}_db.py", base / f"{servicer}_validation.py"]
        if f.exists()
    ]

    scan_files = _collect_flow_imports(legacy_root, entry_files)

    global_seen: set[str] = set()
    all_hits: list[SqlHit] = []
    for f in scan_files:
        file_hits = extract_sql_hits(f, legacy_root, servicer, remit_date)
        for h in file_hits:
            if h.sha not in global_seen:
                global_seen.add(h.sha)
                all_hits.append(h)

    return all_hits, scan_files


def _hits_to_plan_entries(
    hits: list[SqlHit], servicer: str, legacy_root: Path
) -> list[ExportPlanEntry]:
    """Convert SqlHit list to ExportPlanEntry list for _plan_index.json."""
    entries: list[ExportPlanEntry] = []
    for h in hits:
        logical = f"{servicer}__{h.owner}_{h.sha}"
        entries.append(
            ExportPlanEntry(
                logical_name=logical,
                source_module=h.file_rel,
                source_function=h.owner,
                sql=h.sql_template,
                filter_hints=h.placeholders,
                notes=h.notes,
            )
        )
    return entries


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def cmd_plan(args: argparse.Namespace) -> int:  # noqa: C901
    # Compute defaults for optional path args
    _tool_dir = Path(__file__).parent
    _repo_root = _tool_dir.parent
    if args.legacy_root is None:
        args.legacy_root = str(_repo_root.parent / "PrefectFlow")
    if args.out is None:
        args.out = str(_repo_root / "baselines" / args.servicer / args.remit_date / "input_snapshots")

    legacy_root = Path(args.legacy_root).resolve()
    out_dir = Path(args.out).resolve()
    queries_dir = out_dir / "_export_queries"
    template_dir = queries_dir / "template"
    template_dir.mkdir(parents=True, exist_ok=True)

    scan_ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --- Enhanced scan (import-walking, multi-pattern) ---
    all_hits, scan_files = build_export_plan_enhanced(
        legacy_root, args.servicer, args.remit_date
    )

    if not all_hits:
        print(
            f"[ERR] no SQL extracted from {legacy_root}/flow/remit_validation/"
            f"{args.servicer}_*.py (including transitive imports)",
            file=sys.stderr,
        )
        return 2

    # --- Min-expected check ---
    min_expected: int = getattr(args, "min_expected", 5)
    if len(all_hits) < min_expected:
        print(
            f"[ERR] only {len(all_hits)} SQL strings found; "
            f"expected >= {min_expected} (--min-expected). "
            "Check that the legacy_root path is correct and flow/ files are readable.",
            file=sys.stderr,
        )
        return 3

    # --- Write SQL template files under template/ ---
    written_new: list[str] = []
    written_kept: list[str] = []
    for h in all_hits:
        clean = re.sub(r"[^a-zA-Z0-9_]", "_", h.owner).strip("_")
        fname = f"{args.servicer}__{clean}_{h.sha}.sql"
        sql_file = template_dir / fname

        mrc_flag = "MRC-relevant" if h.mrc_relevant else "non-MRC (other servicer)"
        header = (
            f"-- auto-extracted by tools/freeze_snapshot.py plan (v{TOOL_VERSION})\n"
            f"-- source: {h.file_rel} :: {h.owner} (lines {h.start_line}–{h.end_line})\n"
            f"-- servicer: {args.servicer}  flag: {mrc_flag}\n"
            f"-- remit_date: {args.remit_date}\n"
            f"-- pattern: {h.pattern_type}\n"
            f"-- placeholders to resolve: "
            f"{', '.join(h.placeholders) if h.placeholders else '(none)'}\n"
        )
        if h.placeholders:
            header += "-- placeholder hints:\n"
            for k, v in h.placeholders.items():
                header += f"--   {k}: {v}\n"
        header += f"-- notes: {h.notes}\n\n"

        content = header + h.sql_template + "\n"

        if sql_file.exists() and sql_file.read_text(encoding="utf-8") == content:
            written_kept.append(fname)
        else:
            sql_file.write_text(content, encoding="utf-8")
            written_new.append(fname)

    # --- Resolve templates (if --resolve) ---
    resolved_paths_by_sha: dict[str, list[str]] = {}
    resolved_errors: list[str] = []
    bindings: dict[str, str] = {}
    fanout: dict[str, list[dict[str, str]]] = {}

    if getattr(args, "resolve", False):
        bindings_path = Path(args.bindings) if args.bindings else None
        bindings, fanout = load_bindings(bindings_path)
        resolved_dir = queries_dir / "resolved"
        resolved_dir.mkdir(parents=True, exist_ok=True)

        gen_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        for h in all_hits:
            if not h.mrc_relevant:
                continue
            clean = re.sub(r"[^a-zA-Z0-9_]", "_", h.owner).strip("_")
            base_fname = f"{args.servicer}__{clean}_{h.sha}"
            template_rel = f"_export_queries/template/{base_fname}.sql"

            try:
                variants = resolve_template(h.owner, h.sql_template, bindings, fanout)
            except ValueError as exc:
                resolved_errors.append(str(exc))
                resolved_paths_by_sha[h.sha] = []
                continue

            paths: list[str] = []
            for suffix, resolved_sql, used in variants:
                fname2 = f"{base_fname}{suffix}.sql"
                bindings_comment = ", ".join(f"{k}={v}" for k, v in sorted(used.items()))
                header = (
                    f"-- TEMPLATE: {template_rel}\n"
                    f"-- BINDINGS: {bindings_comment if bindings_comment else '(none)'}\n"
                    f"-- GENERATED: {gen_date}\n"
                    f"-- REVIEW BEFORE RUNNING\n\n"
                )
                content2 = header + resolved_sql + "\n"
                out_file = resolved_dir / fname2
                out_file.write_text(content2, encoding="utf-8")
                paths.append(f"_export_queries/resolved/{fname2}")

            resolved_paths_by_sha[h.sha] = paths

    resolved_total = sum(len(v) for v in resolved_paths_by_sha.values())

    # --- Write _coverage.md ---
    coverage_md = build_coverage_md(
        all_hits, scan_files, legacy_root, args.servicer, args.remit_date, scan_ts,
        resolve_enabled=bool(getattr(args, "resolve", False)),
        bindings=bindings,
        fanout=fanout,
        resolved_count=resolved_total,
    )
    coverage_path = queries_dir / "_coverage.md"
    coverage_path.write_text(coverage_md, encoding="utf-8")

    # --- Write _plan_index.json ---
    plan_entries_json = []
    for h in all_hits:
        clean = re.sub(r"[^a-zA-Z0-9_]", "_", h.owner).strip("_")
        fname2 = f"{args.servicer}__{clean}_{h.sha}.sql"
        template_rel = f"_export_queries/template/{fname2}"
        r_paths = resolved_paths_by_sha.get(h.sha, [])
        plan_entries_json.append({
            "logical_name": f"{args.servicer}__{h.owner}_{h.sha}",
            "source_module": h.file_rel,
            "source_function": h.owner,
            "sql": h.sql_template,
            "filter_hints": h.placeholders,
            "notes": h.notes,
            "mrc_relevant": h.mrc_relevant,
            "template_path": template_rel,
            "resolved_paths": r_paths,
        })

    plan_index = out_dir / "_plan_index.json"
    plan_index.write_text(
        json.dumps(
            {
                "manifest_version": MANIFEST_VERSION,
                "tool_version": TOOL_VERSION,
                "servicer": args.servicer,
                "remit_date": args.remit_date,
                "scan_timestamp": scan_ts,
                "legacy_root": str(legacy_root),
                "files_scanned": [
                    str(f.relative_to(legacy_root)).replace("\\", "/")
                    for f in scan_files
                ],
                "total_sql_strings": len(all_hits),
                "mrc_relevant_count": sum(1 for h in all_hits if h.mrc_relevant),
                "resolve_enabled": bool(getattr(args, "resolve", False)),
                "resolved_count": resolved_total,
                "entries": plan_entries_json,
                "hits": [asdict(h) for h in all_hits],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    mrc_count = sum(1 for h in all_hits if h.mrc_relevant)
    print(
        f"[OK] scan complete: {len(all_hits)} SQL strings found "
        f"({mrc_count} MRC-relevant) across {len(scan_files)} file(s)"
    )
    if written_new:
        print(f"     wrote {len(written_new)} new template SQL(s) under {template_dir}")
    if written_kept:
        print(f"     kept {len(written_kept)} unchanged template SQL(s)")
    if getattr(args, "resolve", False):
        print(f"     wrote {resolved_total} resolved SQL file(s) under {queries_dir / 'resolved'}")
        if resolved_errors:
            print(f"     [WARN] {len(resolved_errors)} resolution error(s):", file=sys.stderr)
            for e in resolved_errors:
                print(f"       - {e}", file=sys.stderr)
    print(f"     wrote _coverage.md → {coverage_path}")
    print(f"     wrote _plan_index.json → {plan_index}")
    print()
    print("[NEXT] 1) review _export_queries/_coverage.md and each template/*.sql")
    print("       2) resolve all `{...}` placeholders and `input_*` bare-string placeholders")
    print("       3) run `freeze_snapshot.py export` from a host with Redshift access")
    return 0


# ---------------------------------------------------------------------------
# Verify helpers
# ---------------------------------------------------------------------------

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_coverage_md_mrc_owners(coverage_path: Path) -> list[str]:
    """Extract MRC-relevant owner names from _coverage.md table rows (lines with ✅)."""
    owners: list[str] = []
    for line in coverage_path.read_text(encoding="utf-8").splitlines():
        if "| ✅ |" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        non_empty = [p for p in parts if p]
        if len(non_empty) >= 2:
            owner_raw = non_empty[1]  # backtick-quoted in md: `owner_name`
            owner = owner_raw.strip("`")
            if owner:
                owners.append(owner)
    return owners


def _compute_expected_logical_names(plan_entries: list[dict]) -> list[str]:
    """Derive expected manifest logical_names from MRC-relevant plan_index entries.

    Fan-out entries (multiple resolved_paths) produce one expected name per variant
    (the SQL file stem without extension). Non-fan-out entries use their logical_name.
    """
    names: list[str] = []
    for entry in plan_entries:
        if not entry.get("mrc_relevant"):
            continue
        resolved = entry.get("resolved_paths", [])
        if len(resolved) > 1:
            for rpath in resolved:
                names.append(Path(rpath).stem)
        else:
            names.append(entry["logical_name"])
    return names


def _run_verify_checks(  # noqa: C901
    out_dir: Path,
    servicer: str,
    remit_date: str,
    strict: bool,
    verbose: bool,
) -> tuple[list[dict], int]:
    """Run all verify checks C1–C8. Returns (check_results, exit_code)."""
    checks: list[dict] = []

    def record(check_id: str, passed: bool, message: str, details: list[str] | None = None) -> None:
        checks.append({
            "check": check_id,
            "passed": passed,
            "message": message,
            "details": details or [],
        })

    queries_dir = out_dir / "_export_queries"
    coverage_path = queries_dir / "_coverage.md"
    plan_index_path = out_dir / "_plan_index.json"
    manifest_path = out_dir / "_manifest.json"
    bindings_path = out_dir / "_bindings.json"

    # --- Load _plan_index.json ---
    plan_entries: list[dict] = []
    if plan_index_path.exists():
        try:
            plan_data = json.loads(plan_index_path.read_text(encoding="utf-8"))
            plan_entries = plan_data.get("entries", [])
        except Exception as exc:
            record("C0-preflight", False, f"Cannot parse _plan_index.json: {exc}")

    # --- Load _coverage.md (best-effort; used for C1 supplemental check) ---
    coverage_owners: list[str] = []
    if coverage_path.exists():
        try:
            coverage_owners = _parse_coverage_md_mrc_owners(coverage_path)
        except Exception:
            pass

    # --- Load _manifest.json ---
    manifest_entries: list[dict] = []
    manifest_exists = manifest_path.exists()
    if manifest_exists:
        try:
            manifest_raw = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(manifest_raw, list):
                manifest_entries = manifest_raw
            elif isinstance(manifest_raw, dict):
                manifest_entries = manifest_raw.get("entries", [])
        except Exception as exc:
            manifest_exists = False
            record("C0-preflight", False, f"Cannot parse _manifest.json: {exc}")

    if not manifest_exists:
        for cid in ["C1-coverage-parity", "C2-schema-completeness",
                    "C3-file-existence-checksum", "C4-sql-hash-binding",
                    "C5-schema-sanity", "C6-fanout-consistency"]:
            record(cid, False, "_manifest.json does not exist — run export first")
        if strict:
            record("C7-bindings-doc", False, "_manifest.json does not exist")
            record("C8-storage-policy", False, "_manifest.json does not exist")
        return checks, 1

    manifest_by_name: dict[str, dict] = {
        e.get("logical_name", ""): e for e in manifest_entries
    }

    # ---- C1: Coverage parity ----
    expected_names = _compute_expected_logical_names(plan_entries)
    missing_from_manifest = [n for n in expected_names if n not in manifest_by_name]
    orphan_in_manifest = [n for n in manifest_by_name if n and n not in expected_names]

    if not missing_from_manifest and not orphan_in_manifest:
        record("C1-coverage-parity", True,
               f"All {len(expected_names)} expected datasets present; no orphans")
    else:
        details: list[str] = []
        if missing_from_manifest:
            details.append(
                f"Missing from manifest ({len(missing_from_manifest)}): "
                + ", ".join(missing_from_manifest)
            )
        if orphan_in_manifest:
            details.append(
                f"Orphan in manifest ({len(orphan_in_manifest)}): "
                + ", ".join(orphan_in_manifest)
            )
        record("C1-coverage-parity", False,
               f"{len(missing_from_manifest)} missing, {len(orphan_in_manifest)} orphan(s)",
               details)

    # ---- C2: Manifest schema completeness ----
    _REQUIRED_FIELDS = [
        "logical_name", "source", "export_sql_path", "filter",
        "exported_at", "exporter", "format", "path",
        "row_count", "column_count", "columns", "sha256_file", "sha256_canonical_rows",
    ]
    c2_errors: list[str] = []
    for entry in manifest_entries:
        name = entry.get("logical_name") or "<unnamed>"
        for fld in _REQUIRED_FIELDS:
            val = entry.get(fld)
            if val is None:
                c2_errors.append(f"{name}: '{fld}' is null/missing")
            elif isinstance(val, str) and not val:
                c2_errors.append(f"{name}: '{fld}' is empty string")
            elif fld == "columns" and isinstance(val, list) and not val:
                c2_errors.append(f"{name}: 'columns' is empty list")

        rc = entry.get("row_count")
        if rc is not None and (not isinstance(rc, (int, float)) or rc <= 0):
            c2_errors.append(f"{name}: row_count must be > 0, got {rc!r}")
        cc = entry.get("column_count")
        if cc is not None and (not isinstance(cc, (int, float)) or cc <= 0):
            c2_errors.append(f"{name}: column_count must be > 0, got {cc!r}")

        sha_file = entry.get("sha256_file")
        if sha_file and not _SHA256_RE.match(str(sha_file)):
            c2_errors.append(f"{name}: sha256_file is not a 64-char hex: {sha_file!r}")

        sha_rows = entry.get("sha256_canonical_rows")
        if sha_rows is not None and sha_rows != "__skipped__":
            if not _SHA256_RE.match(str(sha_rows)):
                c2_errors.append(
                    f"{name}: sha256_canonical_rows is not 64-char hex "
                    f"or '__skipped__': {sha_rows!r}"
                )

    if not c2_errors:
        record("C2-schema-completeness", True,
               f"All {len(manifest_entries)} entries pass schema check")
    else:
        record("C2-schema-completeness", False,
               f"{len(c2_errors)} schema violation(s)", c2_errors[:20])

    # ---- C3: File existence + checksum ----
    c3_errors: list[str] = []
    for entry in manifest_entries:
        name = entry.get("logical_name") or "<unnamed>"
        file_path_raw = entry.get("path", "")
        if file_path_raw:
            fp = Path(file_path_raw)
            file_path = fp if fp.is_absolute() else out_dir / fp
            if not file_path.exists():
                c3_errors.append(f"{name}: data file not found: {file_path_raw}")
            else:
                sha_file = entry.get("sha256_file")
                if sha_file and _SHA256_RE.match(str(sha_file)):
                    actual_sha = _sha256_of_file(file_path)
                    if actual_sha != sha_file:
                        c3_errors.append(
                            f"{name}: sha256_file mismatch "
                            f"(expected {sha_file[:8]}…, got {actual_sha[:8]}…)"
                        )
        sql_path_raw = entry.get("export_sql_path", "")
        if sql_path_raw:
            sp = Path(sql_path_raw)
            sql_path = sp if sp.is_absolute() else out_dir / sp
            if not sql_path.exists():
                c3_errors.append(f"{name}: SQL file not found: {sql_path_raw}")

    if not c3_errors:
        record("C3-file-existence-checksum", True,
               f"All {len(manifest_entries)} data + SQL files verified")
    else:
        record("C3-file-existence-checksum", False,
               f"{len(c3_errors)} file/checksum error(s)", c3_errors[:20])

    # ---- C4: SQL hash binding (light; only checks optional sql_sha256 field) ----
    c4_errors: list[str] = []
    for entry in manifest_entries:
        name = entry.get("logical_name") or "<unnamed>"
        sql_path_raw = entry.get("export_sql_path", "")
        sql_sha = entry.get("sql_sha256")
        if sql_path_raw and sql_sha:
            sp = Path(sql_path_raw)
            sql_path = sp if sp.is_absolute() else out_dir / sp
            if sql_path.exists():
                actual = hashlib.sha256(sql_path.read_bytes()).hexdigest()
                if actual != sql_sha:
                    c4_errors.append(
                        f"{name}: sql_sha256 mismatch "
                        f"(expected {sql_sha[:8]}…, got {actual[:8]}…)"
                    )

    if not c4_errors:
        record("C4-sql-hash-binding", True,
               f"SQL hash check passed (optional field; {len(manifest_entries)} entries)")
    else:
        record("C4-sql-hash-binding", False,
               f"{len(c4_errors)} SQL hash mismatch(es)", c4_errors)

    # ---- C5: Schema sanity ----
    c5_errors: list[str] = []
    for entry in manifest_entries:
        name = entry.get("logical_name") or "<unnamed>"
        columns = entry.get("columns", [])
        column_count = entry.get("column_count")
        if column_count is not None and isinstance(columns, list):
            if len(columns) != int(column_count):
                c5_errors.append(
                    f"{name}: column_count={column_count} but len(columns)={len(columns)}"
                )
        if isinstance(columns, list):
            col_names: list[str] = []
            for i, col in enumerate(columns):
                if not isinstance(col, dict):
                    c5_errors.append(f"{name}: columns[{i}] is not a dict")
                    continue
                cname = col.get("name", "")
                dtype = col.get("dtype", "")
                if not cname:
                    c5_errors.append(f"{name}: columns[{i}].name is empty")
                else:
                    col_names.append(cname)
                if not dtype:
                    c5_errors.append(f"{name}: columns[{i}].dtype is empty")
            if len(col_names) != len(set(col_names)):
                dupes = list({n for n in col_names if col_names.count(n) > 1})
                c5_errors.append(f"{name}: duplicate column names: {dupes}")

    if not c5_errors:
        record("C5-schema-sanity", True,
               f"All {len(manifest_entries)} entries pass schema sanity")
    else:
        record("C5-schema-sanity", False,
               f"{len(c5_errors)} schema sanity violation(s)", c5_errors[:20])

    # ---- C6: Resolved-vs-template consistency ----
    c6_errors: list[str] = []
    for entry in plan_entries:
        if not entry.get("mrc_relevant"):
            continue
        resolved = entry.get("resolved_paths", [])
        if len(resolved) > 1:
            for rpath in resolved:
                variant_name = Path(rpath).stem
                if variant_name not in manifest_by_name:
                    c6_errors.append(
                        f"Fan-out variant missing from manifest: {variant_name}"
                    )

    if not c6_errors:
        record("C6-fanout-consistency", True,
               "All fan-out variants present in manifest")
    else:
        record("C6-fanout-consistency", False,
               f"{len(c6_errors)} fan-out variant(s) missing", c6_errors)

    # ---- C7: Bindings doc (--strict only) ----
    if strict:
        c7_errors: list[str] = []
        if not bindings_path.exists():
            c7_errors.append("_bindings.json does not exist")
        else:
            try:
                bindings_data = json.loads(bindings_path.read_text(encoding="utf-8"))
                bd_bindings: dict[str, str] = bindings_data.get("bindings", {})
                resolved_dir = queries_dir / "resolved"
                if resolved_dir.exists():
                    for sql_file in sorted(resolved_dir.glob("*.sql")):
                        content = sql_file.read_text(encoding="utf-8")
                        for line in content.splitlines():
                            if line.startswith("-- BINDINGS:"):
                                bindings_str = line[len("-- BINDINGS:"):].strip()
                                if bindings_str == "(none)":
                                    break
                                for kv in bindings_str.split(", "):
                                    if "=" in kv:
                                        k, v = kv.split("=", 1)
                                        k, v = k.strip(), v.strip()
                                        if k in bd_bindings and bd_bindings[k] != v:
                                            c7_errors.append(
                                                f"{sql_file.name}: binding {k}={v!r} "
                                                f"conflicts with _bindings.json ({k}={bd_bindings[k]!r})"
                                            )
                                break
            except Exception as exc:
                c7_errors.append(f"Cannot parse _bindings.json: {exc}")

        if not c7_errors:
            record("C7-bindings-doc", True,
                   "_bindings.json present and consistent with resolved SQL headers")
        else:
            record("C7-bindings-doc", False,
                   f"{len(c7_errors)} bindings inconsistency(ies)", c7_errors)

    # ---- C8: Storage policy (--strict only) ----
    if strict:
        c8_errors: list[str] = []
        gitignore_path: Path | None = None
        for parent in [out_dir, *out_dir.parents]:
            candidate = parent / ".gitignore"
            if candidate.exists():
                gitignore_path = candidate
                break

        if gitignore_path is None:
            c8_errors.append("No .gitignore found in directory tree")
        else:
            gi_text = gitignore_path.read_text(encoding="utf-8")
            if "parquet/" not in gi_text and "*.parquet" not in gi_text:
                c8_errors.append(".gitignore has no rule for parquet/ or *.parquet")
            if "csv/" not in gi_text and "*.csv" not in gi_text:
                c8_errors.append(".gitignore has no rule for csv/ or *.csv")

        for entry in manifest_entries:
            name = entry.get("logical_name") or "<unnamed>"
            fmt = entry.get("format", "")
            epath = entry.get("path", "")
            if fmt and epath:
                ext = Path(epath).suffix.lower()
                if fmt == "parquet" and ext != ".parquet":
                    c8_errors.append(
                        f"{name}: format=parquet but path has extension {ext!r}"
                    )
                elif fmt == "csv" and ext != ".csv":
                    c8_errors.append(
                        f"{name}: format=csv but path has extension {ext!r}"
                    )

        if not c8_errors:
            record("C8-storage-policy", True,
                   ".gitignore rules + format/extension consistency verified")
        else:
            record("C8-storage-policy", False,
                   f"{len(c8_errors)} storage policy violation(s)", c8_errors)

    # --- Compute exit code ---
    _strict_ids = {"C7-bindings-doc", "C8-storage-policy"}
    core_failed = any(not c["passed"] and c["check"] not in _strict_ids for c in checks)
    strict_failed = any(not c["passed"] and c["check"] in _strict_ids for c in checks)

    if core_failed:
        return checks, 1
    if strict_failed:
        return checks, 2
    return checks, 0


def cmd_verify(args: argparse.Namespace) -> int:
    _tool_dir = Path(__file__).parent
    _repo_root = _tool_dir.parent
    if args.out is None:
        args.out = str(
            _repo_root / "baselines" / args.servicer / args.remit_date / "input_snapshots"
        )

    out_dir = Path(args.out).resolve()
    verbose: bool = getattr(args, "verbose", False)
    strict: bool = getattr(args, "strict", False)
    json_out: bool = getattr(args, "json", False)

    print(f"[verify] servicer={args.servicer}  remit-date={args.remit_date}")
    print(f"[verify] snapshot dir: {out_dir}")
    if strict:
        print("[verify] --strict mode: C7 and C8 enabled")
    print()

    checks, exit_code = _run_verify_checks(
        out_dir, args.servicer, args.remit_date, strict, verbose
    )

    for check in checks:
        icon = "✅" if check["passed"] else "❌"
        print(f"  {icon}  {check['check']}: {check['message']}")
        if verbose and check["details"]:
            for detail in check["details"]:
                print(f"       • {detail}")

    print()
    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    print(f"[verify] {passed}/{total} checks passed")

    if exit_code == 0:
        print("[verify] ✅ All checks passed — snapshot is ready.")
    elif exit_code == 2:
        print("[verify] ⚠️  Strict-mode checks (C7/C8) failed; core checks passed.")
    else:
        print("[verify] ❌ Checks failed — snapshot is NOT ready for G2a close.")
        print()
        print("[OPERATOR] What's still missing:")
        for check in checks:
            if not check["passed"]:
                print(f"  {check['check']}: {check['message']}")
                for detail in check["details"][:5]:
                    print(f"    → {detail}")

    if json_out:
        report = {
            "servicer": args.servicer,
            "remit_date": args.remit_date,
            "snapshot_dir": str(out_dir),
            "strict": strict,
            "checks": checks,
            "passed": passed,
            "total": total,
            "exit_code": exit_code,
        }
        report_path = out_dir / "_verify_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[verify] report written → {report_path}")

    return exit_code


def cmd_export(args: argparse.Namespace) -> int:
    _tool_dir = Path(__file__).parent
    _repo_root = _tool_dir.parent
    if args.legacy_root is None:
        args.legacy_root = str(_repo_root.parent / "PrefectFlow")
    if args.out is None:
        args.out = str(_repo_root / "baselines" / args.servicer / args.remit_date / "input_snapshots")

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
    p_plan.add_argument("--servicer", choices=["mrc"], default="mrc")
    p_plan.add_argument("--remit-date", default="2026-04-30", dest="remit_date")
    p_plan.add_argument("--legacy-root", default=None, dest="legacy_root")
    p_plan.add_argument("--out", default=None)
    p_plan.add_argument(
        "--min-expected",
        type=int,
        default=5,
        dest="min_expected",
        help="Fail if fewer than N SQL strings are found (default: 5)",
    )
    p_plan.add_argument(
        "--resolve",
        action="store_true",
        default=True,
        help="Resolve placeholders to anchor values (default: on)",
    )
    p_plan.add_argument(
        "--no-resolve",
        action="store_false",
        dest="resolve",
        help="Skip placeholder resolution",
    )
    p_plan.add_argument(
        "--bindings",
        default=None,
        help="Path to a _bindings.json file (default: built-in MRC 2026-04-30 bindings)",
    )
    p_plan.set_defaults(func=cmd_plan)

    p_exp = sub.add_parser("export", help="execute the plan against Redshift (operator step)")
    p_exp.add_argument("--servicer", choices=["mrc"], default="mrc")
    p_exp.add_argument("--remit-date", default="2026-04-30", dest="remit_date")
    p_exp.add_argument("--legacy-root", default=None, dest="legacy_root")
    p_exp.add_argument("--out", default=None)
    p_exp.add_argument("--redshift-conn", default=os.environ.get("REDSHIFT_URL"))
    p_exp.add_argument("--also-csv", action="store_true")
    p_exp.set_defaults(func=cmd_export)

    p_ver = sub.add_parser(
        "verify",
        help="validate a populated input_snapshots/ folder (no Redshift needed)",
    )
    p_ver.add_argument("--servicer", choices=["mrc"], default="mrc")
    p_ver.add_argument("--remit-date", default="2026-04-30", dest="remit_date")
    p_ver.add_argument("--out", default=None,
                       help="path to input_snapshots/ dir (default: baselines/<servicer>/<remit-date>/input_snapshots)")
    p_ver.add_argument("--strict", action="store_true",
                       help="also run C7 (_bindings.json) and C8 (storage policy) checks")
    p_ver.add_argument("--verbose", "-v", action="store_true",
                       help="print per-entry details for failed checks")
    p_ver.add_argument("--json", action="store_true",
                       help="write machine-readable report to _verify_report.json")
    p_ver.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
