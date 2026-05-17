# Business rules whitebox convention

Business rules live in YAML at two levels — validator-level and column-level — and are always **bilingual**.

## Two levels

### Validator-level (in `whitebox/validators/<servicer>/<name>.yaml`)

| Field | Required | Meaning |
|---|---|---|
| `rule_en` / `rule_zh` | yes | What this validator does, in business language. 1-3 sentences. |
| `rule_business_impact_en` / `_zh` | optional | If wrong, what business decision/process is affected. |

### Column-level (in `sheets/<sheet>.yaml` under `columns.<col>`)

| Field | Required | Meaning |
|---|---|---|
| `rule_en` / `rule_zh` | yes | How this specific column is derived, in business language. |
| `business_impact_en` / `_zh` | optional | If wrong, what's the consequence. |

## Writing style

- **Audience = business analyst, not developer.** Avoid jargon (`JOIN`, `CTE`) — say "match", "combine".
- **Lead with the "what", not the "how".**
- **Bilingual fidelity.** EN and ZH say the same thing — do not let one drift. When the user writes in Chinese, preserve verbatim and translate to EN.
- **One thought per rule.** Multiple cases go on separate lines under the same `rule_en`/`rule_zh`.

## Linking to known deltas

If a rule intentionally differs from the original `PrefectFlow` behavior, record it in `docs/known-deltas.md` and reference from the rule:

```yaml
rule_en: |
  Sum of monthly principal payments for active loans.
  (Known delta: KD-007 — original system included withdrawn loans by mistake.)
```
