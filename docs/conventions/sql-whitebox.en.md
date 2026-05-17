# SQL whitebox convention

Every validator's original SQL is extracted from the read-only `PrefectFlow` source repo into a `.sql` file alongside its YAML:

```
whitebox/validators/<servicer>/<name>.sql
```

## Extraction rules

1. **Preserve original semantics.** Copy SQL exactly — do not refactor or rename aliases.
2. **Single statement per file.** If the original chains statements, split (e.g. `_setup.sql`, `_main.sql`) and reference the main from YAML.
3. **Top comment cites source.** Start with `-- Extracted from: <file>:<line>`.
4. **Parameter placeholders.** Convert f-string / `.format()` placeholders to standard SQL params (`:param` or `?`). Document in YAML's `description_*`.

## Why this matters

The `.sql` file serves three roles at once:

- **Documentation** — syntax-highlighted on the validator's page.
- **Lineage input** — sqlglot parses it to auto-extract column-level lineage.
- **Implementation reference** — the sibling `.py` must produce the same rows on the frozen Parquet snapshot.

If `.sql` and `.py` diverge, the diff harness catches it.
