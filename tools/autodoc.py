"""Auto-documentation generator.

Reads the YAML registry and renders bilingual MkDocs pages:
    docs/validators/<servicer>/<name>.{en,zh}.md  -- validator angle
    docs/sheets/<sheet>.{en,zh}.md                -- sheet angle (column drill-down)
    docs/lineage.{en,zh}.md                       -- Mermaid DAG

Run before `mkdocs build`. Pages are overwritten on each run; never edit
generated files by hand.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from tools.registry import Registry, Sheet, Validator, load_all

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
TEMPLATES_DIR = Path(__file__).parent / "templates"


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(disabled_extensions=("md",)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_validator(env: Environment, v: Validator, reg: Registry) -> None:
    tpl_en = env.get_template("validator.en.md.j2")
    tpl_zh = env.get_template("validator.zh.md.j2")
    sheets = [reg.sheets[s] for s in v.data["related_sheets"] if s in reg.sheets]
    ctx: dict[str, Any] = {"v": v.data, "sql": v.sql or "", "sheets": sheets}
    base = DOCS_DIR / "validators" / v.data["servicer"] / v.data["name"]
    _write(base.with_suffix(".en.md"), tpl_en.render(**ctx))
    _write(base.with_suffix(".zh.md"), tpl_zh.render(**ctx))


def render_sheet(env: Environment, s: Sheet, reg: Registry) -> None:
    tpl_en = env.get_template("sheet.en.md.j2")
    tpl_zh = env.get_template("sheet.zh.md.j2")
    ctx: dict[str, Any] = {"s": s.data, "columns": s.columns, "reg": reg}
    base = DOCS_DIR / "sheets" / s.name
    _write(base.with_suffix(".en.md"), tpl_en.render(**ctx))
    _write(base.with_suffix(".zh.md"), tpl_zh.render(**ctx))


def render_lineage(env: Environment, reg: Registry) -> None:
    tpl_en = env.get_template("lineage.en.md.j2")
    tpl_zh = env.get_template("lineage.zh.md.j2")
    edges: list[tuple[str, str]] = []
    for v in reg.validators.values():
        for tbl in v.data.get("source_tables", []):
            edges.append((tbl, v.id))
        for s in v.data.get("related_sheets", []):
            edges.append((v.id, f"sheet::{s}"))
    ctx: dict[str, Any] = {"edges": edges, "reg": reg}
    _write(DOCS_DIR / "lineage.en.md", tpl_en.render(**ctx))
    _write(DOCS_DIR / "lineage.zh.md", tpl_zh.render(**ctx))


def render_index_pages(reg: Registry) -> None:
    """Index pages listing all validators / all sheets."""
    # validators index
    lines_en = ["# Validators\n", "Auto-generated index.\n"]
    lines_zh = ["# Validators\n", "自动生成索引。\n"]
    by_servicer: dict[str, list[Validator]] = {}
    for v in reg.validators.values():
        by_servicer.setdefault(v.data["servicer"], []).append(v)
    for servicer, vs in sorted(by_servicer.items()):
        lines_en.append(f"\n## {servicer}\n")
        lines_zh.append(f"\n## {servicer}\n")
        for v in sorted(vs, key=lambda x: x.data["name"]):
            link = f"{servicer}/{v.data['name']}.md"
            lines_en.append(f"- [{v.data['title_en']}]({link})")
            lines_zh.append(f"- [{v.data['title_zh']}]({link})")
    _write(DOCS_DIR / "validators" / "index.en.md", "\n".join(lines_en) + "\n")
    _write(DOCS_DIR / "validators" / "index.zh.md", "\n".join(lines_zh) + "\n")
    # sheets index
    lines_en = ["# Sheets\n", "Auto-generated index. Click any sheet, then any column, to see its full logic.\n"]
    lines_zh = ["# Sheets\n", "自动生成索引。点击任一 sheet 进入，再点击任一 column 查看完整逻辑。\n"]
    for sname, s in sorted(reg.sheets.items()):
        lines_en.append(f"- [{sname}]({sname}.md) — {s.data['business_meaning_en']}")
        lines_zh.append(f"- [{sname}]({sname}.md) —— {s.data['business_meaning_zh']}")
    _write(DOCS_DIR / "sheets" / "index.en.md", "\n".join(lines_en) + "\n")
    _write(DOCS_DIR / "sheets" / "index.zh.md", "\n".join(lines_zh) + "\n")


def clean_generated() -> None:
    """Remove previously generated dirs so deleted validators/sheets disappear."""
    for sub in ("validators", "sheets"):
        target = DOCS_DIR / sub
        if target.exists():
            shutil.rmtree(target)
    for fname in ("lineage.en.md", "lineage.zh.md"):
        p = DOCS_DIR / fname
        if p.exists():
            p.unlink()


def main() -> int:
    reg = load_all()
    if reg.errors:
        for e in reg.errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    clean_generated()
    env = _env()
    for v in reg.validators.values():
        render_validator(env, v, reg)
    for s in reg.sheets.values():
        render_sheet(env, s, reg)
    render_lineage(env, reg)
    render_index_pages(reg)
    print(f"Generated docs for {len(reg.validators)} validators, {len(reg.sheets)} sheets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
