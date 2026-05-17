# Registry conventions

Two-layer YAML metadata that drives the whole whitebox site.

## Files

- `whitebox/validators/<servicer>/<name>.yaml` — one per validator.
- `whitebox/validators/<servicer>/<name>.sql` — raw SQL extracted from the original source code.
- `whitebox/validators/<servicer>/<name>.py` — Python implementation of the same logic.
- `sheets/<sheet_name>.yaml` — one per report sheet, with per-column metadata.

## Required fields — validator YAML

| Field | Notes |
|---|---|
| `id` | `<servicer>/<name>`, lowercase + underscores. Globally unique. |
| `servicer` / `name` | Match `id`. |
| `title_en` / `title_zh` | Short titles for the doc site. |
| `related_sheets` | Sheet names this validator produces. |
| `source_tables` | Upstream Redshift tables (`schema.table`). |
| `source_citation` | `<file>:<line>` pointing into the read-only source repo. |
| `rule_en` / `rule_zh` | Business rule, plain prose, bilingual. |
| `sql_file` | Relative path to the `.sql` (or `null` for pure-Python). |

Optional: `description_*`, `rule_business_impact_*`, `tags`.

## Required fields — sheet YAML

| Field | Notes |
|---|---|
| `sheet` | Sheet name as it appears in the gold XLSX. |
| `business_meaning_*` | Bilingual one-line summary. |
| `producing_validators` | Validator IDs that contribute columns. |
| `columns.<col>.type` | `string`/`integer`/`float`/`decimal`/`date`/`datetime`/`boolean`/`json`. |
| `columns.<col>.rule_en` / `rule_zh` | Bilingual business rule **for this column**. |

Optional: `format`, `business_impact_*`, `sample_values`, `related_validator`.

## Auto-filled fields (do not hand-edit)

Populated by `tools/build_lineage.py` (sqlglot) on every doc build:

- `columns.<col>.sources` — upstream `{table, column, transform}`.
- `columns.<col>.expression` — SQL expression that produces the column.

## Validation

Run `python -m tools.registry` to validate all YAMLs and print a tree.
