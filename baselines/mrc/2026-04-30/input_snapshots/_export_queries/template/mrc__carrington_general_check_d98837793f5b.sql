-- auto-extracted by tools/freeze_snapshot.py plan (v2.1)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: carrington_general_check (lines 103–154)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

select
-- Carrington Remittance
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
-- Carrington Daily
, c.interest_rate as intrate_daily
, c.nextduedate as nextduedate_daily
, c.principalbalance as endbal_daily
--check interest_rate
, intrate_remit - intrate_daily as intrate_diff_remitvsdaily
--check nextduedate
, nextduedate_remit - nextduedate_daily as nextduedate_diff_remitvsdaily
-- check begbal remitvsdaily
, begbal_remit - c2.principalbalance as begbal_diff_remitvsdaily
-- check endbal remitvsdaily
, endbal_remit - endbal_daily as endbal_diff_remitvsdaily
-- check upb + deferred upb = total upb
, endbal_remit + deferredupb_remit - totalupb_remit as principal_diff_remit
-- check begbal - endbal = principal_remit
, begbal_remit - endbal_remit + deferredbal_paid_remit - principal_remit as balchg_prin_diff_remit
-- check pandi
--, pandi_remit - (principal_remit + interest_remit) as pandi_diff_remit
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
and c.asofdate = dateadd(day, -1, r.fctrdt)
and c2.asofdate = 'input_pre_month_end'
;
