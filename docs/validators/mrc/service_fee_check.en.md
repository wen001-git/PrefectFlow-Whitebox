# MRC Service Fee Check

**ID**: `mrc/service_fee_check` &nbsp;&nbsp; **Servicer**: `mrc` &nbsp;&nbsp; **Source**: `flow/remit_validation/mrc_validation.py:75`

Loan-level service-fee reconciliation: compare MRC's loan-level remit recap
(portmrcremitloanlevelrecap) against the consolidated portmonth servicefee for each
loan, flagging discrepancies.

## Business rule

For each row in mrc.portmrcremitloanlevelrecap at the current fctrdt, left-join to
port.portmonth (MRC) on (fctrdt, loanid) and to port.portfunding on loanid for dealid
fallback. Output servicefee_remit_raw (from recap), servicefee_portmonth, and their
difference. Any non-zero servicefee_diff indicates an aggregation mismatch.

!!! info "Business impact"
    Service fee errors directly affect servicer revenue recognition.

## Produces sheets

- [MRC_ServiceFee_Check](../../sheets/MRC_ServiceFee_Check.md) — Loan-level service-fee reconciliation: MRC's loan-level remit recap vs the consolidated
portmonth servicefee. Any non-zero diff flags an aggregation mismatch.


## Source tables

- `mrc.portmrcremitloanlevelrecap`
- `port.portmonth`
- `port.portfunding`

*(Pure-Python validator; no extracted SQL file.)*

**Tags**: `mrc`, `service_fee`, `stub`