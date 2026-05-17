# baselines/

Frozen reference XLSX baselines produced by 	ools/freeze_baseline.py.

Structure:
```
baselines/
  <servicer>/
    <remit_date>/
      validation_report.xlsx   # frozen artifact (legacy code on frozen Parquet snapshot)
      manifest.json            # {servicer, remit_date, writer, writer_version, sha256, ...}
```

Contract:
- One folder per (servicer, remit_date) tuple.
- `validation_report.xlsx` is the **truth oracle** for Stage 2 cell-identity acceptance.
- See `docs/mrc/baseline.{zh,en}.md` (chapter 1.6) for the full per-attribute contract.

Currently authored chapters:
- `mrc/2026-04-30/` — placeholder folder; XLSX + manifest to be produced by `tools/freeze_baseline.py` (todo: `mrc-source-baseline`).
