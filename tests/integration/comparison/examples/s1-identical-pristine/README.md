# S1 — identical-pristine: PASS

**Scenario:** C3 pristine mode vs C3 pristine mode (same seed=42)

**Expected verdict:** `PASS` — zero diffs, exit code 0

**Files:**
- `verdict.json` — `verdict: "PASS"`, `summary.major_diff_count: 0`, `summary.minor_diff_count: 0`
- `comparison_report.json` — `summary.identical: true`, empty `diffs` list
- `comparison_report.html` — HTML showing no diffs (baseline = self-test)

## What to look at

Open `verdict.json` and verify `verdict = "PASS"`. The `diffs` list in `comparison_report.json`
should be empty (`[]`). This proves the harness self-test passes when both sides are generated
from the same C3 stub with the same seed.
