# MRC acceptance-allowlist schema

> Audience: developers adding a documented MINOR-diff exception to the
> v9.1 acceptance gate.

This file documents the schema for
`tests/acceptance/mrc/acceptance_minor_diffs_allowlist.json`.

## When to add an entry

You may add an entry **only** when:

1. The MINOR diff is reproducible, understood, and judged acceptable.
2. There is an **ADR** in `decisions.md` explaining why the new system
   intentionally diverges on this dimension (e.g. a documented
   border-color refresh).
3. The diff is **not** a MAJOR diff. MAJOR diffs (`value`, `formula`,
   `merged_cells`, `structure`) are never allowlistable; they always
   fail the gate. The meta-test
   `test_acceptance_gate.test_allowlist_entries_have_required_keys`
   enforces this.

## Required keys

| Key | Type | Meaning |
|---|---|---|
| `sheet` | string | XLSX sheet name (e.g. `MRC_General_Check`). |
| `cell_ref` | string | Column letter + row number (e.g. `B7`). Sheet-level diffs use `""` (empty). |
| `dimension` | string | One of: `format`, `font`, `fill`, `border`, `alignment`, `freeze_panes`, `col_width`, `row_height`, `sheet_view`. |
| `justification` | string | One-sentence why this diff is acceptable. |
| `ADR_ref` | string | Anchor in `decisions.md`, e.g. `2026-05-25 — border style refresh`. |

## Example entry (do NOT commit unless ADR exists)

```json
[
  {
    "sheet": "MRC_General_Check",
    "cell_ref": "B7",
    "dimension": "border",
    "justification": "Renderer applies a thin bottom border on header row to match the corporate template refresh.",
    "ADR_ref": "2026-05-25 — header border style refresh"
  }
]
```

## How the allowlist is consumed

* `tests/acceptance/mrc/test_against_baseline.py` and
  `test_against_legacy_live.py` skip a diff if and only if its
  (`sheet`, `cell_ref`, `dimension`) triple matches an entry.
* `tools/acceptance_gate.py` reports the number of allowlisted vs
  undocumented MINOR diffs in `acceptance_verdict.json` under
  `components.baseline.allowlisted` / `components.legacy_live.allowlisted`.

The file starts as an empty array (`[]`) because the v9.1 baseline
contract is **cell-identical with zero allowlist entries**.
