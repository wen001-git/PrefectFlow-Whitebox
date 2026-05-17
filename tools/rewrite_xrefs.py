"""Bulk rewrite MRC docs to enforce chapter-reference canonicalization.

Per docs/mrc/_chapter-index.md:
- Add H1 with chapter number + bilingual title at top of each file
- Insert Chapter Index snippet after the Purpose/Audience block
- Rewrite inline chapter references to three-element form
"""
import re
from pathlib import Path

DOCS = Path(r"C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox\docs\mrc")

# (number, EN title, ZH title, base filename, H1 phrase)
CHAPTERS = [
    ("1.0", "TOC & Scope", "章节地图与范围", "toc"),
    ("1.1", "Raw Data Layer", "原始数据层", "rawdata"),
    ("1.2", "Dataflow Layer", "数据流层", "dataflow"),
    ("1.3", "Sheet Rendering Layer", "Sheet 渲染层", "sheets"),
    ("1.4", "Field Definitions", "字段定义", "fields"),
    ("1.5", "Validation Rules", "验证规则", "rules"),
    ("1.6", "Baseline XLSX Behavior", "Baseline XLSX 行为", "baseline"),
    ("1.7", "User Review Gate", "用户走读评审", None),
]

EN_NAMES = {num: en for num, en, _, _ in CHAPTERS}
ZH_NAMES = {num: zh for num, _, zh, _ in CHAPTERS}
BASES = {num: base for num, _, _, base in CHAPTERS}

INDEX_ZH = (DOCS / "_chapter-index-snippet.zh.md").read_text(encoding="utf-8")
INDEX_EN = (DOCS / "_chapter-index-snippet.en.md").read_text(encoding="utf-8")

def strip_html_comment(snippet: str) -> str:
    # Remove leading HTML comment block from snippet (the embed instruction)
    return re.sub(r"^<!--.*?-->\s*", "", snippet, count=1, flags=re.DOTALL).strip()

INDEX_ZH_CLEAN = strip_html_comment(INDEX_ZH)
INDEX_EN_CLEAN = strip_html_comment(INDEX_EN)


def cite(num: str, is_zh: bool) -> str:
    title = ZH_NAMES[num] if is_zh else EN_NAMES[num]
    base = BASES[num]
    if base is None:
        return f"{num} {title}"
    suffix = "zh.md" if is_zh else "en.md"
    return f"{num} {title} ({base}.{suffix})"


def rewrite_refs(text: str, is_zh: bool) -> tuple[str, int]:
    """Apply ordered substitutions. Return (new_text, n_changes)."""
    n = 0

    # Pattern 1: ZH "第 1.X 章" → cite
    def sub_zh_chapter(m):
        nonlocal n
        n += 1
        return cite(f"1.{m.group(1)}", is_zh)
    text = re.sub(r"第\s*1\.([0-7])\s*章", sub_zh_chapter, text)

    # Pattern 2: "chapter 1.X" (lower / upper c) — match standalone, optional
    # trailing § or punctuation; do not consume the following content.
    def sub_chapter(m):
        nonlocal n
        n += 1
        return cite(f"1.{m.group(1)}", is_zh)
    text = re.sub(r"\bchapter\s+1\.([0-7])\b(?!\.\d)", sub_chapter,
                  text, flags=re.IGNORECASE)

    # Pattern 3: EN "see 1.X" (not followed by .digit which would be subsection)
    def sub_see(m):
        nonlocal n
        n += 1
        head = "见" if is_zh else "see"
        return f"{head} {cite(f'1.{m.group(1)}', is_zh)}"
    text = re.sub(r"\bsee\s+1\.([0-7])\b(?!\.\d)", sub_see, text)

    # Pattern 4: EN "defined in 1.X"
    def sub_defined(m):
        nonlocal n
        n += 1
        return f"defined in {cite(f'1.{m.group(1)}', is_zh)}"
    text = re.sub(r"\bdefined in 1\.([0-7])\b(?!\.\d)", sub_defined, text)

    # Pattern 5: bare "1.X §" mid-prose (only when not preceded by chapter/見/See
    # — those already handled above). Match: word-boundary, 1.X, space, §
    # Avoid matching version strings like "v1.4" or sub-section "1.4.2".
    def sub_bare_section(m):
        nonlocal n
        n += 1
        return f"{cite(f'1.{m.group(1)}', is_zh)} §"
    # negative lookbehind for letter/digit/period to avoid v1.4, 1.4.2
    text = re.sub(r"(?<![\w.])1\.([0-7])\s+§", sub_bare_section, text)

    return text, n


def insert_index(text: str, is_zh: bool) -> tuple[str, bool]:
    """Insert the Chapter Index snippet just before the first --- separator."""
    snippet = INDEX_ZH_CLEAN if is_zh else INDEX_EN_CLEAN
    if "**MRC 章节索引**" in text or "**MRC chapter index**" in text:
        return text, False  # already inserted
    # Find the first --- on its own line
    m = re.search(r"^---\s*$", text, flags=re.MULTILINE)
    if not m:
        return text, False
    before = text[:m.start()]
    after = text[m.start():]
    new = before.rstrip() + "\n\n" + snippet + "\n\n" + after
    return new, True


def insert_h1(text: str, num: str, is_zh: bool) -> tuple[str, bool]:
    """Ensure top H1 with `# X.Y EN Title / ZH 标题` exists.

    If file already starts with `# 1. ...` (toc style), replace it. Otherwise
    insert above the leading blockquote.
    """
    en = EN_NAMES[num]
    zh = ZH_NAMES[num]
    h1 = f"# {num} {en} / {zh}"
    # Already done?
    if re.search(rf"^# {re.escape(num)} ", text, flags=re.MULTILINE):
        return text, False
    # Replace existing `# 1. ...` at top (toc case)
    m = re.match(r"^# 1\. [^\n]*\n", text)
    if m:
        return h1 + "\n" + text[m.end():], True
    # Otherwise insert at very top
    return h1 + "\n\n" + text, True


def process(path: Path, num: str):
    is_zh = path.name.endswith(".zh.md")
    text = path.read_text(encoding="utf-8")
    orig_len = len(text)

    text, h1_inserted = insert_h1(text, num, is_zh)
    text, idx_inserted = insert_index(text, is_zh) if path.stem.split(".")[0] != "toc" else (text, False)
    text, n_refs = rewrite_refs(text, is_zh)

    path.write_text(text, encoding="utf-8")
    print(f"{path.name:25s}  H1={h1_inserted!s:5s}  Idx={idx_inserted!s:5s}  refs={n_refs:3d}  len={orig_len}→{len(text)}")


# Map base filename to chapter number
NUM_BY_BASE = {
    "toc": "1.0", "rawdata": "1.1", "dataflow": "1.2",
    "sheets": "1.3", "fields": "1.4", "rules": "1.5",
    "baseline": "1.6",
}

def main():
    for p in sorted(DOCS.glob("*.md")):
        if p.name.startswith("_"):
            continue
        base = p.stem.split(".")[0]
        if base not in NUM_BY_BASE:
            continue
        process(p, NUM_BY_BASE[base])


if __name__ == "__main__":
    main()
