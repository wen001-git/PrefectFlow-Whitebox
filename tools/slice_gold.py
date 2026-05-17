"""Slice the gold XLSX into per-sheet JSON files for the diff harness.

Usage:
  python -m tools.slice_gold <gold.xlsx> <out_dir> [--sheet NAME ...]

The output JSON files (`<sheet>.json` each) are an array of `{column: value}` rows
ready to be consumed by `tools/diff_report.py`'s `load_gold(dir)` helper. Values are
normalized: datetimes → ISO strings, NaN → null.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

import openpyxl


def _norm(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    return v


def slice_xlsx(xlsx: Path, out_dir: Path, only_sheets: list[str] | None) -> list[Path]:
    wb = openpyxl.load_workbook(xlsx, data_only=True, read_only=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for ws in wb.worksheets:
        if only_sheets and ws.title not in only_sheets:
            continue
        rows_iter = ws.iter_rows(values_only=True)
        try:
            header = list(next(rows_iter))
        except StopIteration:
            continue
        headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(header)]
        data: list[dict[str, Any]] = []
        for row in rows_iter:
            if row is None or all(v is None for v in row):
                continue
            data.append({headers[i]: _norm(row[i] if i < len(row) else None) for i in range(len(headers))})
        path = out_dir / f"{ws.title}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        written.append(path)
        print(f"  {ws.title}: {len(data)} rows -> {path}")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xlsx", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--sheet", action="append", default=None,
                        help="Limit to these sheet names (repeatable). Default: all sheets.")
    args = parser.parse_args(argv)
    written = slice_xlsx(args.xlsx, args.out_dir, args.sheet)
    print(f"Wrote {len(written)} sheet(s) to {args.out_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
