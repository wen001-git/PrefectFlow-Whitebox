"""Apply same xref canonicalization to progress.md, plan.md, and
test_reports/stage1-mrc-*.md (no Index snippet, no H1 reinforcement —
those files are not part of the docs/mrc/ tree).
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox")
sys.path.insert(0, str(ROOT / "tools"))
from rewrite_xrefs import rewrite_refs  # noqa: E402

# meta files always use ZH form (the project's prose uses ZH/EN mix; default
# to ZH because that's the predominant prose language in these meta docs).
TARGETS = [
    ROOT / "progress.md",
    ROOT / "plan.md",
] + sorted((ROOT / "test_reports").glob("stage1-mrc-*.md"))

for p in TARGETS:
    text = p.read_text(encoding="utf-8")
    new, n = rewrite_refs(text, is_zh=True)
    if n:
        p.write_text(new, encoding="utf-8")
    print(f"{p.relative_to(ROOT)}  refs={n}")
