"""Phase 1 self-test: end-to-end exercise of the doc infrastructure.

Verifies:
1. Registry loads + validates with the placeholder validator and sheet.
2. sqlglot extracts column-level lineage from the placeholder SQL.
3. autodoc renders both validator and sheet pages bilingually.
4. diff_report on gold-vs-gold reports zero deltas.
5. The placeholder Python implementation produces the gold rows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import autodoc, build_lineage, diff_report, registry  # noqa: E402
from whitebox.validators._placeholder.hello import run as placeholder_run  # noqa: E402


def test_registry_loads_clean() -> None:
    reg = registry.load_all()
    assert reg.errors == []
    assert "_placeholder/hello" in reg.validators
    assert "placeholder_hello" in reg.sheets


def test_lineage_extracts_sources(tmp_path: Path) -> None:
    reg = registry.load_all()
    # Run lineage on the placeholder; reload, then check sources populated.
    msgs = build_lineage.build_for_validator(reg, "_placeholder/hello")
    assert msgs, "build_lineage should have written at least one update"
    reg2 = registry.load_all()
    cols = reg2.sheets["placeholder_hello"].columns
    assert cols["loan_id"].get("sources"), "loan_id should have at least one source"
    assert cols["principal_x2"].get("sources"), "principal_x2 should have at least one source"
    # principal_x2 should trace back to public.placeholder_input.principal
    pxs_sources = cols["principal_x2"]["sources"]
    matched = any(
        ("placeholder_input" in (s.get("table") or "") and s.get("column") == "principal")
        for s in pxs_sources
    )
    assert matched, f"sqlglot should trace principal_x2 → principal; got {pxs_sources}"


def test_autodoc_renders_pages() -> None:
    reg = registry.load_all()
    autodoc.clean_generated()
    env = autodoc._env()
    for v in reg.validators.values():
        autodoc.render_validator(env, v, reg)
    for s in reg.sheets.values():
        autodoc.render_sheet(env, s, reg)
    autodoc.render_lineage(env, reg)
    autodoc.render_index_pages(reg)
    base = ROOT / "docs"
    assert (base / "validators" / "_placeholder" / "hello.en.md").exists()
    assert (base / "validators" / "_placeholder" / "hello.zh.md").exists()
    assert (base / "sheets" / "placeholder_hello.en.md").exists()
    assert (base / "sheets" / "placeholder_hello.zh.md").exists()
    en_sheet = (base / "sheets" / "placeholder_hello.en.md").read_text(encoding="utf-8")
    assert "principal_x2" in en_sheet
    assert "placeholder_input" in en_sheet  # source field reference rendered


def test_diff_gold_vs_gold_clean(tmp_path: Path) -> None:
    gold_path = ROOT / "tests" / "fixtures" / "placeholder_gold.json"
    gold = diff_report.load_gold(gold_path)
    diffs = diff_report.diff_all(gold, gold)
    assert all(d.clean for d in diffs), [d.name for d in diffs if not d.clean]


def test_python_impl_matches_gold(tmp_path: Path) -> None:
    inputs = [
        {"loan_id": "L001", "principal": 100000},
        {"loan_id": "L002", "principal": 175000},
    ]
    result = placeholder_run(inputs)
    gold_path = ROOT / "tests" / "fixtures" / "placeholder_gold.json"
    gold = json.loads(gold_path.read_text(encoding="utf-8"))["placeholder_hello"]
    # Compare as sets of tuples (order-insensitive)
    def _norm(r: dict) -> tuple:
        return tuple(sorted(r.items()))
    assert {_norm(r) for r in result} == {_norm(r) for r in gold}


def test_xlsx_round_trip_clean(tmp_path: Path) -> None:
    """Write gold rows to an XLSX, diff that XLSX against the gold JSON, expect clean."""
    gold_path = ROOT / "tests" / "fixtures" / "placeholder_gold.json"
    data = json.loads(gold_path.read_text(encoding="utf-8"))
    xlsx_path = tmp_path / "candidate.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for sheet_name, rows in data.items():
        ws = wb.create_sheet(sheet_name)
        if not rows:
            continue
        headers = list(rows[0].keys())
        ws.append(headers)
        for r in rows:
            ws.append([r.get(h) for h in headers])
    wb.save(xlsx_path)
    candidate = diff_report.load_candidate(xlsx_path)
    gold = diff_report.load_gold(gold_path)
    diffs = diff_report.diff_all(candidate, gold)
    bad = [d for d in diffs if not d.clean]
    assert not bad, [(d.name, d.only_in_candidate, d.only_in_gold) for d in bad]
