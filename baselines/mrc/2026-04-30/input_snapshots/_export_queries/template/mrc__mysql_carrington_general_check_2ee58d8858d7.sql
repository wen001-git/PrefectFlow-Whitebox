-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: mysql_carrington_general_check (lines 157–197)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

select
r.loanid, r.carrington_ln_number, f.dealid
, r.interest_rate as intrate_remit
, r.next_due_date as nextduedate_remit
, r.beginning_balance as begbal_remit
, r.ending_balance as endbal_remit
, r.current_regular_pmt_amt as pandi_expected_remit
, r.principal_payment_actual_prinorcash_received as principal_remit
, r.gross_interest_payment as interest_remit
, r.ending_def_prin as deferredupb_remit
, r.total_upb as totalupb_remit
, r.beginning_def_prin - r.ending_def_prin as deferredbal_paid_remit
, c.interest_rate as intrate_daily
, c.nextduedate as nextduedate_daily
, c.principalbalance as endbal_daily
, r.interest_rate - c.interest_rate as intrate_diff_remitvsdaily
, r.next_due_date - c.nextduedate as nextduedate_diff_remitvsdaily
, r.beginning_balance - c2.principalbalance as begbal_diff_remitvsdaily
, r.ending_balance - c.principalbalance as endbal_diff_remitvsdaily
, r.ending_balance + r.ending_def_prin - r.total_upb as principal_diff_remit
, r.beginning_balance - r.ending_balance + (r.beginning_def_prin - r.ending_def_prin) - r.principal_payment_actual_prinorcash_received as balchg_prin_diff_remit
from
    carrington.portcarringtonremit r
inner join
    port.basic_data_daily_loan_common c
on
    r.loanid = c.loanid
inner join
    port.basic_data_daily_loan_common c2
on
    r.loanid = c2.loanid
left join
    port.portfunding f
on
    r.loanid = f.loanid
where
    r.fctrdt = 'input_fctrdt'
and c.asofdate = DATE_ADD(r.fctrdt, INTERVAL -1 DAY)
and c2.asofdate = 'input_pre_month_end';
