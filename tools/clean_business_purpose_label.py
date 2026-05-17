"""Strip the redundant leading bullet label that duplicates the H3 heading
("业务用途 / Business purpose" / "Business purpose / 业务用途") in the
Business-purpose subsection inserted by tools/insert_business_purpose.py.

Before:
    ### 业务用途 / Business purpose
    - **业务用途 / Business purpose**：整张 Validation Report ...

After:
    ### 业务用途 / Business purpose

    整张 Validation Report ...
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "mrc"

# Match the marker + heading + the first bullet that duplicates the label.
PATTERN_ZH = re.compile(
    r"(<!-- BUSINESS-PURPOSE-V1 -->\n### 业务用途 / Business purpose\n)- \*\*业务用途 / Business purpose\*\*：",
)
PATTERN_EN = re.compile(
    r"(<!-- BUSINESS-PURPOSE-V1 -->\n### Business purpose / 业务用途\n)- \*\*Business purpose\*\*: ",
)


def clean(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n_zh = PATTERN_ZH.subn(r"\1\n", text)
    new_text, n_en = PATTERN_EN.subn(r"\1\n", new_text)
    if n_zh + n_en:
        path.write_text(new_text, encoding="utf-8")
    return n_zh + n_en


def main():
    for p in [
        DOCS / "1.3-sheets.zh.md",
        DOCS / "1.3-sheets.en.md",
        DOCS / "1.4-fields.zh.md",
        DOCS / "1.4-fields.en.md",
    ]:
        n = clean(p)
        print(f"{p.relative_to(ROOT)}: stripped {n} duplicate label(s)")


if __name__ == "__main__":
    main()
