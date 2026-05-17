"""Cleanup pass for meta files (progress.md, plan.md, test_reports/stage1-mrc-*.md)."""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox")
sys.path.insert(0, str(ROOT / "tools"))
from cleanup_xrefs import clean

TARGETS = [ROOT / "progress.md", ROOT / "plan.md"] + sorted(
    (ROOT / "test_reports").glob("stage1-mrc-*.md")
)

for p in TARGETS:
    text = p.read_text(encoding="utf-8")
    new, n = clean(text)
    if n:
        p.write_text(new, encoding="utf-8")
    print(f"{p.relative_to(ROOT).as_posix()}  changes={n}")
