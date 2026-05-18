# Capturing the MRC baseline XLSX

> Audience: an operator with Redshift VPN + HashiCorp Vault token who
> can run the legacy `flow/remit_validation` MRC entrypoint against
> production Redshift.
>
> This document is the "what to do the day G2a unblocks" runbook for
> populating `baselines/mrc/2026-04-30/validation_report.xlsx`, the
> oracle file the v9.1 acceptance gate diffs against.

## When to use this

* The acceptance gate currently treats a missing baseline as
  ENV-SKIP (see `docs/stage2/12.0-acceptance-gate.en.md` §3).
* Once you have a known-good legacy XLSX captured here, every PR's
  acceptance gate will start diffing engine output against this file.
* If the legacy code changes (rare) or `remit_date` rolls forward,
  the baseline must be re-captured and a new ADR appended to
  `decisions.md`.

## One-time prerequisites

1. Working tree clean and on `main`.
2. `.env` populated with `VAULT_ADDR` + `VAULT_TOKEN` per
   `.env.example`.
3. PrefectFlow source repo present at `../PrefectFlow/`
   (a sibling checkout — the source repo is **READ-ONLY**, see
   `AGENTS.md` §3).
4. `uv sync` and a working `python -m whitebox.engine --help`.

## Step 1 — Run the legacy MRC flow

```powershell
python tools\run_legacy_mrc.py `
  --servicer mrc `
  --remit-date 2026-04-30 `
  --out-dir runs\legacy-baseline-capture\
```

Expected outputs:

* `runs\legacy-baseline-capture\validation_report.xlsx`
* `runs\legacy-baseline-capture\run_metadata.json`
* `runs\legacy-baseline-capture\run.log`

If exit code is non-zero, fix the env / Vault problem first; do not
proceed.

## Step 2 — Manual sanity-check the XLSX

Open the captured XLSX in Excel and confirm:

* 5 sheets in this exact order:
  `MRC_Summary_check`, `MRC_General_Check`, `MRC_Advance_Check`,
  `MRC_ServiceFee_Check`, `MRC_Adv_Info`.
* Each sheet has rows (i.e. `mrc_validation.py` did not fall through
  to the empty-DataFrame branch for any validator).
* No obvious data corruption (NaN/inf in numeric cells, mojibake in
  strings).

If anything looks wrong, stop and investigate before promoting.

## Step 3 — Promote into `baselines/`

```powershell
Copy-Item runs\legacy-baseline-capture\validation_report.xlsx `
  baselines\mrc\2026-04-30\validation_report.xlsx
Copy-Item runs\legacy-baseline-capture\run_metadata.json `
  baselines\mrc\2026-04-30\validation_report_metadata.json
```

## Step 4 — Register the checksum

Append the SHA-256 of the captured XLSX to
`baselines\mrc\2026-04-30\CHECKSUMS.txt` (create the file if missing):

```powershell
$xlsx = "baselines\mrc\2026-04-30\validation_report.xlsx"
$hash = (Get-FileHash $xlsx -Algorithm SHA256).Hash.ToLower()
"$hash  validation_report.xlsx" |
  Add-Content baselines\mrc\2026-04-30\CHECKSUMS.txt
```

This is the integrity anchor: if the file ever changes (intentionally
or otherwise) the checksum line must be updated in the same commit.

## Step 5 — Commit + ADR

```powershell
git add baselines\mrc\2026-04-30\
git commit -m "baseline(MRC): capture 2026-04-30 legacy XLSX as v9.1 oracle"
```

Append to `decisions.md`:

```
## YYYY-MM-DD — MRC 2026-04-30 baseline XLSX captured
- Captured by: <operator>
- Legacy source SHA: <git rev-parse HEAD in PrefectFlow checkout>
- SHA-256 of validation_report.xlsx: <hash>
- Acceptance gate will now diff against this file.
```

## Step 6 — Verify the acceptance gate engages

```powershell
python tools\acceptance_gate.py `
  --servicer MRC `
  --remit-date 2026-04-30 `
  --baseline baselines\mrc\2026-04-30\validation_report.xlsx `
  --legacy-mode skip `
  --output runs\acceptance-with-baseline\
```

Expected: `acceptance_verdict.json` shows
`components.baseline.status == "PASS"` (or documented `MINOR_DIFFS`
with allowlist entries) and overall verdict `PASS`. A `MAJOR_DIFFS`
verdict here means the new engine has actually regressed against
the legacy oracle — file an issue, do **not** edit the baseline to
"make the test pass".

## When credentials lapse

Leave the captured baseline in place. The gate continues to use it.
Re-capture only when:

1. Legacy code in `../PrefectFlow/flow/remit_validation/` changes in
   a way that legitimately alters the XLSX, or
2. `remit_date` advances and the new system pivots to a new baseline.
