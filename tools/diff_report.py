"""Diff harness: compare a candidate XLSX against gold JSON snapshots.

Normalizes data types (NaN → null; floats compared with tolerance), then
diffs per-sheet on (sorted_row, column, value) tuples. Outputs an HTML
report + machine-readable JSON summary. Exit code: 0 = clean, non-zero
on first mismatch.

Used by the harness self-test (gold vs gold = zero deltas) and during
every validator/sheet implementation cycle.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import openpyxl

FLOAT_TOLERANCE = 1e-6


def _norm_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, float):
        if math.isnan(v):
            return None
        return float(v)
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    return v


def _floats_equal(a: Any, b: Any, tol: float) -> bool:
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    return abs(float(a) - float(b)) <= tol


def normalize_sheet(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normed = [{k: _norm_value(v) for k, v in r.items()} for r in rows]
    # Sort by tuple of all (key, str(value)) for deterministic ordering
    return sorted(normed, key=lambda r: [(k, "" if v is None else str(v)) for k, v in sorted(r.items())])


def xlsx_to_sheets(path: Path) -> dict[str, list[dict[str, Any]]]:
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    out: dict[str, list[dict[str, Any]]] = {}
    for ws in wb.worksheets:
        rows_iter = ws.iter_rows(values_only=True)
        try:
            header = next(rows_iter)
        except StopIteration:
            out[ws.title] = []
            continue
        header = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(header)]
        rows: list[dict[str, Any]] = []
        for row in rows_iter:
            if row is None or all(v is None for v in row):
                continue
            rows.append({header[i]: row[i] if i < len(row) else None for i in range(len(header))})
        out[ws.title] = rows
    return out


def load_gold(path: Path) -> dict[str, list[dict[str, Any]]]:
    if path.is_dir():
        out: dict[str, list[dict[str, Any]]] = {}
        for jf in sorted(path.glob("*.json")):
            with jf.open(encoding="utf-8") as f:
                out[jf.stem] = json.load(f)
        return out
    with path.open(encoding="utf-8") as f:
        return dict(json.load(f))


def load_candidate(path: Path) -> dict[str, list[dict[str, Any]]]:
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        return xlsx_to_sheets(path)
    return load_gold(path)


@dataclass
class SheetDiff:
    name: str
    only_in_candidate: list[dict[str, Any]] = field(default_factory=list)
    only_in_gold: list[dict[str, Any]] = field(default_factory=list)
    value_mismatches: list[dict[str, Any]] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.only_in_candidate or self.only_in_gold or self.value_mismatches)


def diff_sheet(
    name: str,
    candidate_rows: list[dict[str, Any]],
    gold_rows: list[dict[str, Any]],
    tol: float,
) -> SheetDiff:
    d = SheetDiff(name=name)
    cand = normalize_sheet(candidate_rows)
    gold = normalize_sheet(gold_rows)

    def _row_key(r: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(sorted(r.items()))

    cand_keys = {_row_key(r): r for r in cand}
    gold_keys = {_row_key(r): r for r in gold}
    only_cand_keys = set(cand_keys) - set(gold_keys)
    only_gold_keys = set(gold_keys) - set(cand_keys)

    # Float-tolerant fallback: for keys differing only by floats within tol, mark as equal
    leftover_cand = list(only_cand_keys)
    leftover_gold = list(only_gold_keys)
    matched_via_tol: set[Any] = set()
    for ck in list(leftover_cand):
        for gk in list(leftover_gold):
            cr = cand_keys[ck]
            gr = gold_keys[gk]
            if set(cr.keys()) != set(gr.keys()):
                continue
            all_match = True
            for k in cr:
                if cr[k] == gr[k]:
                    continue
                if not _floats_equal(cr[k], gr[k], tol):
                    all_match = False
                    break
            if all_match:
                matched_via_tol.add(ck)
                leftover_gold.remove(gk)
                break

    for ck in leftover_cand:
        if ck not in matched_via_tol:
            d.only_in_candidate.append(cand_keys[ck])
    for gk in leftover_gold:
        d.only_in_gold.append(gold_keys[gk])
    return d


def diff_all(
    candidate: dict[str, list[dict[str, Any]]],
    gold: dict[str, list[dict[str, Any]]],
    tol: float = FLOAT_TOLERANCE,
    only_sheets: list[str] | None = None,
) -> list[SheetDiff]:
    sheets = set(candidate) | set(gold)
    if only_sheets:
        sheets &= set(only_sheets)
    results: list[SheetDiff] = []
    for s in sorted(sheets):
        results.append(diff_sheet(s, candidate.get(s, []), gold.get(s, []), tol))
    return results


def render_html(diffs: list[SheetDiff], candidate: Path, gold: Path) -> str:
    parts: list[str] = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Diff report</title>",
        "<style>body{font-family:sans-serif;margin:2em}h2{margin-top:2em}",
        ".ok{color:green}.bad{color:#b00}table{border-collapse:collapse;margin:.5em 0}",
        "td,th{border:1px solid #ccc;padding:.2em .5em;font-size:90%}</style></head><body>",
        f"<h1>Diff report</h1><p>candidate: <code>{html.escape(str(candidate))}</code><br>",
        f"gold: <code>{html.escape(str(gold))}</code></p>",
    ]
    total_bad = sum(0 if d.clean else 1 for d in diffs)
    parts.append(
        f"<p><strong>{len(diffs)} sheets diffed, {total_bad} with mismatches.</strong></p>"
    )
    for d in diffs:
        cls = "ok" if d.clean else "bad"
        status = "CLEAN" if d.clean else "MISMATCH"
        parts.append(f"<h2 class='{cls}'>{html.escape(d.name)} — {status}</h2>")
        if d.clean:
            continue
        for label, rows in (
            ("Only in candidate", d.only_in_candidate),
            ("Only in gold", d.only_in_gold),
        ):
            if not rows:
                continue
            parts.append(f"<h3>{label} ({len(rows)})</h3>")
            if rows:
                headers = sorted({k for r in rows for k in r})
                parts.append("<table><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr>")
                for r in rows[:50]:
                    parts.append(
                        "<tr>"
                        + "".join(f"<td>{html.escape(str(r.get(h)))}</td>" for h in headers)
                        + "</tr>"
                    )
                parts.append("</table>")
                if len(rows) > 50:
                    parts.append(f"<p><em>... {len(rows) - 50} more rows truncated</em></p>")
    parts.append("</body></html>")
    return "".join(parts)


def render_summary(diffs: list[SheetDiff]) -> dict[str, Any]:
    return {
        "sheets": [
            {
                "name": d.name,
                "clean": d.clean,
                "only_in_candidate": len(d.only_in_candidate),
                "only_in_gold": len(d.only_in_gold),
            }
            for d in diffs
        ],
        "all_clean": all(d.clean for d in diffs),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="Candidate XLSX or JSON directory")
    parser.add_argument("gold", type=Path, help="Gold JSON file or directory")
    parser.add_argument("--out", type=Path, default=Path("diff_report.html"))
    parser.add_argument("--summary", type=Path, default=Path("diff_report.json"))
    parser.add_argument("--tol", type=float, default=FLOAT_TOLERANCE)
    parser.add_argument("--sheet", action="append", default=None, help="Limit to these sheet names")
    args = parser.parse_args(argv)

    candidate = load_candidate(args.candidate)
    gold = load_gold(args.gold)
    diffs = diff_all(candidate, gold, tol=args.tol, only_sheets=args.sheet)
    args.out.write_text(render_html(diffs, args.candidate, args.gold), encoding="utf-8")
    args.summary.write_text(json.dumps(render_summary(diffs), indent=2), encoding="utf-8")
    all_clean = all(d.clean for d in diffs)
    print(("CLEAN" if all_clean else "MISMATCH") + f" — wrote {args.out} and {args.summary}")
    return 0 if all_clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
