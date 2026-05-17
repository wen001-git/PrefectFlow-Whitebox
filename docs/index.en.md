# PrefectFlow Whitebox

Welcome to the whitebox documentation site for the **remit_validation**
pipeline of `PrefectFlow`.

This site is **auto-generated** from per-validator and per-sheet YAML
metadata. Every column on every report sheet has its own logic card
showing source fields, SQL expression, bilingual business rule, sample
values, and lineage.

## Where to start

- **Validators** — code-level view, grouped by servicer.
- **Sheets** — report-output view; the primary entry point for business
  users. Click any column to see its full logic.
- **Lineage** — full DAG (dataset + column layers).
- **Known deltas** — intentional differences from the original system,
  with business reason.

## Scope

**Whitebox**: Redshift data → validators → report sheets.

**Black-boxed** (out of scope): vendor raw files → `flow/servicer_data/`
ingestion → Redshift. May be added in a future iteration.

## Pilot

This site is being populated **MRC-first** (5 validators). Other
servicers follow after the MRC pilot gate passes.

---

中文版请切换语言（顶部菜单 → 中文）。
