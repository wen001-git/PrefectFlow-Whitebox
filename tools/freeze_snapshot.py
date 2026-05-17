"""tools/freeze_snapshot.py — G2a snapshot freezer (binding).

Freeze the exact MRC validator input dataset to local files so Stage 2
development is decoupled from live Redshift. See session plan.md section 4.2
for the binding spec and `decisions.md` 2026-05-17 entry "G2 redefinition".

This tool has two subcommands:

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

Folder layout produced under `<out>`:

    <out>/
      _export_queries/
        template/<logical_name>.sql            (plan + export)
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
TOOL_VERSION = "2.0"

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

    # --- Write _coverage.md ---
    coverage_md = build_coverage_md(
        all_hits, scan_files, legacy_root, args.servicer, args.remit_date, scan_ts
    )
    coverage_path = queries_dir / "_coverage.md"
    coverage_path.write_text(coverage_md, encoding="utf-8")

    # --- Write _plan_index.json ---
    plan_entries = _hits_to_plan_entries(all_hits, args.servicer, legacy_root)
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
                "entries": [asdict(e) for e in plan_entries],
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
    print(f"     wrote _coverage.md → {coverage_path}")
    print(f"     wrote _plan_index.json → {plan_index}")
    print()
    print("[NEXT] 1) review _export_queries/_coverage.md and each template/*.sql")
    print("       2) resolve all `{...}` placeholders and `input_*` bare-string placeholders")
    print("       3) run `freeze_snapshot.py export` from a host with Redshift access")
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
    p_plan.add_argument(
        "--min-expected",
        type=int,
        default=5,
        dest="min_expected",
        help="Fail if fewer than N SQL strings are found (default: 5)",
    )
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
