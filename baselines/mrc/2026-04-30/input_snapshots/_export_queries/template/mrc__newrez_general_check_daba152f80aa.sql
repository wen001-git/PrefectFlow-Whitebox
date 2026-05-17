-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: newrez_general_check (lines 313–375)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

select
-- from Remittance
r.loanid, r.shellpoint_ln, f.dealid,
case when coalesce(i.principalreceived, 0) != 0 or coalesce(i.interestreceived, 0) != 0 then 'Y' else 'N' end as interim_flag
, r.net_int_rate as intrate_remit
, r.actl_beg_prin_bal as begbal_remit
, r.actl_end_prin_bal as endbal_remit
, r.actl_prin_amt + r.serv_curt_amt_1 + r.serv_curt_amt_2 + r.serv_curt_amt_3 + r.pif_amt
+ r.non_interest_bearing_deferred_principal_curt_amt + r.non_interest_bearing_deferred_paid_in_full_amount as principal_remit
, r.actl_net_int as interest_remit
, principal_remit + interest_remit + coalesce(i.principalreceived, 0) + coalesce(i.interestreceived, 0) as pandi_remit
, r.ending_non_interest_bearing_deferred_principal_bal  as deferredprincipal_remit
, r.endingdeferredinterestbalance as deferredint_remit
-- from Payment
, p.nextduedate
, p.principalbalance as endbal_daily
, p.deferredprincipalbalance as deferredprincipal_daily
, p.deferredinterestbalance as deferredint_daily
, p.schedule_pandi_daily as pandiexpected_daily
, p.principalpaidmtd as principalreceived_daily
, p.interestpaidmtd as interestreceived_daily
, p.principalpaidmtd + p.interestpaidmtd as pandireceived_daily
-- from General
, p.interest_rate as intrate_daily
, p.bal_prin_original /((1-(1/(1+intrate_daily/1200)^p.originalterm))/(intrate_daily/1200)) as pandi_calc
, p.delq_status as delinquency_status_mba
-- check difference
, begbal_remit - endbal_remit - principal_remit as prin_bal_diff_remit
, p2.deferredprincipalbalance - p.deferredprincipalbalance as deferredprincipal_chg_daily
, intrate_remit - intrate_daily as intrate_diff_remitvsdaily
, endbal_remit - endbal_daily as endbal_diff_remitvsdaily
, deferredprincipal_remit - deferredprincipal_daily as deferredprincipal_diff_remitvsdaily
, deferredint_remit - deferredint_daily as deferredint_diff_remitvsdaily
, pandi_remit - pandireceived_daily as pandi_diff_remitvsdaily
, case when p.nextduedate =r.borr_next_pay_due_date then 0 else 1 end as nextduedate_diff_remitvsdaily
, case when pandiexpected_daily = 0 then null else pandi_remit / pandiexpected_daily end as pandi_paid_times_remit
, case when pandiexpected_daily = 0 then null else pandireceived_daily / pandiexpected_daily end as pandi_paid_times_daily
-- will add in the future to check next due date change vs how many payment we receive.
from
    newrez.portnewrezremitwf r
inner join
    port.basic_data_daily_loan_common p
on
    r.loanid = p.loanid
inner join
    port.basic_data_daily_loan_common p2
on
    r.loanid = p2.loanid
and r.fctrdt = 'input_fctrdt'
and p.asofdate = 'input_curr_month_end'
and p2.asofdate = 'input_pre_month_end'
left join
    port.portinterim i
on
    r.loanid = i.loanid
and r.fctrdt = i.fctrdt
left join
    port.portfunding f
on
    r.loanid = f.loanid
;
