# Placeholder: Hello validator

**ID**: `_placeholder/hello` &nbsp;&nbsp; **Servicer**: `_placeholder` &nbsp;&nbsp; **Source**: `whitebox/validators/_placeholder/hello.py:1`

Synthetic validator used only to self-test the Phase 1 doc
infrastructure (registry, lineage, autodoc, harness). Not a real
business validator. Will be deleted before Phase 3 cleanup.

## Business rule

For each row in placeholder_input, copy loan_id and compute principal_x2 = principal * 2.
!!! info "Business impact"
    If broken, the placeholder sheet shows wrong doubled values; no business impact.

## Produces sheets

- [placeholder_hello](../../sheets/placeholder_hello.md) — Selftest sheet — doubled principals for placeholder loans.

## Source tables

- `public.placeholder_input`

## SQL

```sql
-- Extracted from: whitebox/validators/_placeholder/hello.py:1
-- Placeholder validator SQL — selftest only.
SELECT
    loan_id        AS loan_id,
    principal * 2  AS principal_x2
FROM public.placeholder_input

```

**Tags**: `selftest`, `placeholder`