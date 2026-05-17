"""Post-rewrite cleanup:
1. Collapse duplicate-name patterns like `<Title> (<file>.md) <Title> (<file>.md)` → `<Title> (<file>.md)`
2. Add a space between CJK char and a citation `<num> <Title>` and after closing `.md)`.
"""
import re
from pathlib import Path

DOCS = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox\docs\mrc")

# Title patterns (any title char + " (" + base + ".(en|zh).md)")
DUP_RX = re.compile(
    r"(\b1\.[0-7]\s+[^()\n]+?\s+\(([a-z]+)\.(en|zh)\.md\))(\s+[^()\n]+?\s+\(\2\.\3\.md\))",
)

CJK = r"[\u4e00-\u9fff]"
# Insert space between CJK and "1.X "
PRE_RX = re.compile(rf"({CJK})(1\.[0-7]\s)")
# Insert space between ".md)" and CJK
POST_RX = re.compile(rf"(\.(?:en|zh)\.md\))({CJK})")


def clean(text: str) -> tuple[str, int]:
    n = 0
    def collapse(m):
        nonlocal n
        n += 1
        return m.group(1)
    text = DUP_RX.sub(collapse, text)

    def pre(m):
        nonlocal n
        n += 1
        return f"{m.group(1)} {m.group(2)}"
    text = PRE_RX.sub(pre, text)

    def post(m):
        nonlocal n
        n += 1
        return f"{m.group(1)} {m.group(2)}"
    text = POST_RX.sub(post, text)

    return text, n


for p in sorted(DOCS.glob("*.md")):
    if p.name.startswith("_"):
        continue
    text = p.read_text(encoding="utf-8")
    new, n = clean(text)
    if n:
        p.write_text(new, encoding="utf-8")
    print(f"{p.name:25s}  changes={n:3d}")
