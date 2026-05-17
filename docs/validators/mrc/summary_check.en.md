# MRC Summary Check

**ID**: `mrc/summary_check` &nbsp;&nbsp; **Servicer**: `mrc` &nbsp;&nbsp; **Source**: `flow/remit_validation/mrc_validation.py:8`

Single-row aggregate sums of all MRC loans' remit-month financials for sanity-checking
the total volume reported by the servicer.

## Business rule

Sum 13 financial fields (principal/interest received, escrow & corp advance changes,
service fees, sub-remit & total remit, beginning & ending balance) across all rows in
port.portmonth where servicer='MRC' and fctrdt = current factor date. Single-row output
with asofdate = remit_date.

!!! info "Business impact"
    If totals are wrong, the entire MRC monthly remittance file is suspect.

## Produces sheets

- [MRC_Summary_check](../../sheets/MRC_Summary_check.md) — Single-row aggregate of all MRC loans' remit-month financials for sanity-checking the
total volume reported by the servicer.


## Source tables

- `port.portmonth`

*(Pure-Python validator; no extracted SQL file.)*

**Tags**: `mrc`, `summary`, `stub`