# S2 — value-diff: MAJOR_DIFFS

**Scenario:** Baseline workbook (5 sheets) vs copy with `Summary!B3 = 9999.99` (sentinel value)

**Expected verdict:** `MAJOR_DIFFS` — exit code 2

**Files:**
- `verdict.json` — `verdict: "MAJOR_DIFFS"`, `summary.major_diff_count >= 1`
- `comparison_report.json` — `diffs` list contains entry with `category: "value"`, `sheet: "Summary"`, `row: 3`, `col: "B"`
- `comparison_report.html` — HTML highlighting the single value diff

## What to look at

Open `comparison_report.json` and find the diff entry:
```json
{
  "sheet": "Summary",
  "row": 3,
  "col": "B",
  "category": "value",
  "severity": "major",
  "legacy": "<original baseline value>",
  "new": "9999.99"
}
```

This proves the harness catches a deliberate single-cell value change.
