# MRC Advance Balance Check (remit vs daily)

**ID**: `mrc/check_adv_balance` &nbsp;&nbsp; **Servicer**: `mrc` &nbsp;&nbsp; **Source**: `flow/remit_validation/servicer_validation_with_portdaily.py:583`

Loan-level advance-balance reconciliation: for each MRC loan, compare escrow advance,
recoverable corp advance, and non-recoverable corp advance balances between remit
(portmonth changes) and our daily snapshot (prev vs curr month-end deltas).

## Business rule

Join portmonth (remit) with previous- and current-month basic_data_daily_loan_common
snapshots for MRC. For each loan, compute the daily-snapshot change (curr - prev) for
escrow / recoverable corp / non-recoverable corp advance balances and compare against
the servicer-reported _chg fields. The "_diff_remitvsdaily" output should reconcile to
near zero when both sides agree.

!!! info "Business impact"
    Mismatched advances directly affect cash flow projections for investors.

## Produces sheets

- [MRC_Advance_Check](../../sheets/MRC_Advance_Check.md) — Loan-level advance-balance reconciliation for MRC. For each loan, escrow / recoverable
corp / non-recoverable corp advance balances are compared between remit (portmonth _chg
fields) and daily snapshot (curr - prev month-end). Non-zero "_diff_remitvsdaily" =
potential servicer reporting issue.


## Source tables

- `port.portmonth`
- `port.basic_data_daily_loan_common`
- `port.portfunding`

*(Pure-Python validator; no extracted SQL file.)*

**Tags**: `mrc`, `advance`, `remit_vs_daily`, `stub`