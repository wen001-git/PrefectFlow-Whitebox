# MRC General Info Check (remit vs daily)

**ID**: `mrc/check_general_info` &nbsp;&nbsp; **Servicer**: `mrc` &nbsp;&nbsp; **Source**: `flow/remit_validation/servicer_validation_with_portdaily.py:635`

Loan-level reconciliation: compare key loan attributes (interest rate, next due date,
begin/end balance, deferred principal/interest, P&I) between the servicer's remit
report (port.portmonth) and our internal daily snapshot (basic_data_daily_loan_common).

## Business rule

Join portmonth (remit master) with two snapshots of basic_data_daily_loan_common
(previous month-end & current month-end) for MRC. For each loan emit "_remit" and
"_daily" values plus their "_diff_remitvsdaily" deltas. Non-zero deltas in interest
rate / next due date / balances / deferred amounts / P&I schedule flag potential
servicer reporting errors.

!!! info "Business impact"
    Mismatches feed downstream investor reporting reconciliation.

## Produces sheets

- [MRC_General_Check](../../sheets/MRC_General_Check.md) — Loan-level reconciliation of key loan attributes between the servicer's remit report
(port.portmonth) and our internal daily snapshot (basic_data_daily_loan_common).
"_remit" and "_daily" pairs with their "_diff_remitvsdaily" deltas flag servicer
reporting errors.


## Source tables

- `port.portmonth`
- `port.basic_data_daily_loan_common`
- `port.basic_data_monthly_loan_common`
- `port.portfunding`

*(Pure-Python validator; no extracted SQL file.)*

**Tags**: `mrc`, `general`, `remit_vs_daily`, `stub`