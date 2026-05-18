"""End-of-stage doc tests: heading skeleton alignment + source citation existence."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox")
SRC = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow")
DOC_DIR = ROOT / "docs"
ARCHIVE_DIR = DOC_DIR / "_archived" / "pre-mrc-pivot"

# Pairs are (zh_relpath, en_relpath) relative to DOC_DIR.
PAIRS = [
    # G2a A6 — Redshift dependency catalog
    ("mrc/_g2a-redshift-dependencies.zh.md", "mrc/_g2a-redshift-dependencies.en.md"),
    # v9.1 placeholder registry + 6 pending-servicer stubs
    ("_status/servicers-registry.zh.md", "_status/servicers-registry.en.md"),
    # MRC chapter (Stage 1, in progress)
    ("mrc/1.0-toc.zh.md", "mrc/1.0-toc.en.md"),
    ("mrc/1.1-rawdata.zh.md", "mrc/1.1-rawdata.en.md"),
    ("mrc/1.2-dataflow.zh.md", "mrc/1.2-dataflow.en.md"),
    ("mrc/1.3-sheets.zh.md", "mrc/1.3-sheets.en.md"),
    ("mrc/1.4-fields.zh.md", "mrc/1.4-fields.en.md"),
    ("mrc/1.5-rules.zh.md", "mrc/1.5-rules.en.md"),
    ("mrc/1.6-baseline.zh.md", "mrc/1.6-baseline.en.md"),
    ("arvest/_pending.zh.md", "arvest/_pending.en.md"),
    ("cc5/_pending.zh.md", "cc5/_pending.en.md"),
    ("selene/_pending.zh.md", "selene/_pending.en.md"),
    ("sls/_pending.zh.md", "sls/_pending.en.md"),
    ("scattered/_pending.zh.md", "scattered/_pending.en.md"),
    ("dataflow/_pending.zh.md", "dataflow/_pending.en.md"),
    # Stage 2 design docs
    ("stage2/6.0-ui-architecture.zh.md", "stage2/6.0-ui-architecture.en.md"),
    ("stage2/7.0-module-boundaries.zh.md", "stage2/7.0-module-boundaries.en.md"),
    ("stage2/8.0-servicer-onboarding.zh.md", "stage2/8.0-servicer-onboarding.en.md"),
    ("stage2/9.0-dev-plan.zh.md", "stage2/9.0-dev-plan.en.md"),
    ("stage2/10.0-validation-strategy.zh.md", "stage2/10.0-validation-strategy.en.md"),
    # archived v8 chapters (kept under check so their alignment/citations don't bit-rot)
    ("_archived/pre-mrc-pivot/toc.zh.md", "_archived/pre-mrc-pivot/toc.en.md"),
    ("_archived/pre-mrc-pivot/overall-flow.zh.md", "_archived/pre-mrc-pivot/overall-flow.en.md"),
    ("_archived/pre-mrc-pivot/carrington.zh.md", "_archived/pre-mrc-pivot/carrington.en.md"),
    ("_archived/pre-mrc-pivot/shellpoint.zh.md", "_archived/pre-mrc-pivot/shellpoint.en.md"),
]

# 1) heading skeleton (depth sequence) must match
def heading_depths(p: Path) -> list[int]:
    return [len(m.group(1)) for line in p.read_text(encoding="utf-8").splitlines()
            if (m := re.match(r"^(#+)\s", line))]

align_fail = 0
for zh, en in PAIRS:
    z, e = heading_depths(DOC_DIR / zh), heading_depths(DOC_DIR / en)
    if z == e:
        print(f"ALIGN OK  : {zh} vs {en}  ({len(z)} headings)")
    else:
        print(f"ALIGN FAIL: {zh} ({len(z)} headings) vs {en} ({len(e)} headings)")
        print(f"   zh: {z}")
        print(f"   en: {e}")
        align_fail += 1

# 2) source citations: file.py:LINE or file.py:LINE-LINE inside docs must resolve
cite_re = re.compile(r"`([a-zA-Z_][\w/\\\.]*\.py):(\d+)(?:-(\d+))?`")

PRUNE = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache", ".ruff_cache", "site"}
_basename_cache: dict[str, list[Path]] = {}
def _all_py() -> dict[str, list[Path]]:
    if _basename_cache:
        return _basename_cache
    for dirpath, dirnames, filenames in __import__("os").walk(SRC):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        for fn in filenames:
            if fn.endswith(".py"):
                _basename_cache.setdefault(fn, []).append(Path(dirpath) / fn)
    return _basename_cache

ok = miss_file = miss_line = 0
miss_examples: list[str] = []
for f in DOC_DIR.rglob("*.md"):
    text = f.read_text(encoding="utf-8")
    for m in cite_re.finditer(text):
        rel, l1, l2 = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        full = SRC / rel
        if not full.exists():
            alt = ROOT / rel
            if alt.exists():
                full = alt
        if not full.exists():
            cands = _all_py().get(Path(rel).name, [])
            if len(cands) == 1:
                full = cands[0]
            elif len(cands) > 1:
                match = [c for c in cands if str(c).replace("\\","/").endswith(rel.replace("\\","/"))]
                if len(match) == 1:
                    full = match[0]
                else:
                    miss_file += 1
                    miss_examples.append(f"MISS file (ambiguous): {rel} -> {len(cands)} candidates (in {f.name})")
                    continue
            else:
                miss_file += 1
                miss_examples.append(f"MISS file: {rel} (in {f.name})")
                continue
        nlines = sum(1 for _ in full.open(encoding="utf-8", errors="ignore"))
        if l1 < 1 or l2 > nlines:
            miss_line += 1
            miss_examples.append(f"MISS line: {rel}:{l1}-{l2} (file has {nlines} lines, in {f.name})")
        else:
            ok += 1

print(f"\nCitations: {ok} PASS / {miss_file} missing-file / {miss_line} out-of-range")
for ex in miss_examples[:20]:
    print(" ", ex)

# exit non-zero on any P0 failure
if align_fail or miss_file or miss_line:
    sys.exit(1)
sys.exit(0)
