# Sheets

Auto-generated index. Click any sheet, then any column, to see its full logic.

- [MRC_Adv_Info](MRC_Adv_Info.md) — Bucketed advance amounts at the description + transaction_code level for three advance
categories (non-recoverable corp, recoverable corp, escrow), with prior-month MoM ratio.

- [MRC_Advance_Check](MRC_Advance_Check.md) — Loan-level advance-balance reconciliation for MRC. For each loan, escrow / recoverable
corp / non-recoverable corp advance balances are compared between remit (portmonth _chg
fields) and daily snapshot (curr - prev month-end). Non-zero "_diff_remitvsdaily" =
potential servicer reporting issue.

- [MRC_General_Check](MRC_General_Check.md) — Loan-level reconciliation of key loan attributes between the servicer's remit report
(port.portmonth) and our internal daily snapshot (basic_data_daily_loan_common).
"_remit" and "_daily" pairs with their "_diff_remitvsdaily" deltas flag servicer
reporting errors.

- [MRC_ServiceFee_Check](MRC_ServiceFee_Check.md) — Loan-level service-fee reconciliation: MRC's loan-level remit recap vs the consolidated
portmonth servicefee. Any non-zero diff flags an aggregation mismatch.

- [MRC_Summary_check](MRC_Summary_check.md) — Single-row aggregate of all MRC loans' remit-month financials for sanity-checking the
total volume reported by the servicer.

- [placeholder_hello](placeholder_hello.md) — Selftest sheet — doubled principals for placeholder loans.
