-- TEMPLATE: _export_queries/template/mrc__mrc_general_check_62a675d7e6c6.sql
-- BINDINGS: input_curr_month_end=2026-04-30, input_fctrdt=2026-05-01, input_pre_month_end=2026-03-31
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

with r as (
    select *
    from port.portmonth
    where servicer = 'MRC'
      and fctrdt = '2026-05-01'
),
p as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = '2026-04-30'
      and servicer = 'MRC'
),
p2 as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = '2026-03-31'
      and servicer = 'MRC'
)
select r.loanid,
       r.svcloanid as mrc_ln,
       coalesce(r.dealid, f.dealid) as dealid,
       r.intrate as intrate_remit,
       r.nextduedate as nextduedate_remit,
       r.prevbal as begbal_remit,
       r.balance as endbal_remit,
       r.principalreceived as principal_remit,
       r.interestreceived as interest_remit,
       r.pandireceived as pandi_remit,
       r.deferredprin as deferredprincipal_remit,
       r.deferredint as deferredint_remit,
       p.nextduedate as nextduedate_daily,
       p2.principalbalance as begbal_daily,
       p.principalbalance as endbal_daily,
       p.deferredprincipalbalance as deferredprincipal_daily,
       p.deferredinterestbalance as deferredint_daily,
       p.schedule_pandi_daily as pandiexpected_daily,
       p.principalpaidmtd as principalreceived_daily,
       p.interestpaidmtd as interestreceived_daily,
       case
           when p.principalpaidmtd is null and p.interestpaidmtd is null then null
           else coalesce(p.principalpaidmtd, 0) + coalesce(p.interestpaidmtd, 0)
           end as pandireceived_daily,
       p.interest_rate as intrate_daily,
       p.delq_status as delinquency_status_mba,
       r.prevbal - r.balance - coalesce(r.principalreceived, 0) as prin_bal_diff_remit,
       r.prevbal - p2.principalbalance as begbal_diff_remitvsdaily,
       r.balance - p.principalbalance as endbal_diff_remitvsdaily,
       coalesce(r.deferredprin, 0) - coalesce(p.deferredprincipalbalance, 0) as deferredprincipal_diff_remitvsdaily,
       coalesce(r.deferredint, 0) - coalesce(p.deferredinterestbalance, 0) as deferredint_diff_remitvsdaily,
       r.intrate - p.interest_rate as intrate_diff_remitvsdaily,
       case when r.nextduedate = p.nextduedate then 0 else 1 end as nextduedate_diff_remitvsdaily,
       case
           when p.principalpaidmtd is null and p.interestpaidmtd is null then null
           else coalesce(r.pandireceived, 0) - (coalesce(p.principalpaidmtd, 0) + coalesce(p.interestpaidmtd, 0))
           end as pandi_diff_remitvsdaily,
       coalesce(mc.sched_pandi, r.pandi) - p.schedule_pandi_daily as pandi_schedule_diff_remitvsdaily,
       case when coalesce(p.schedule_pandi_daily, 0) = 0 then null else r.pandireceived / p.schedule_pandi_daily end as pandi_paid_times_remit,
       case
           when coalesce(p.schedule_pandi_daily, 0) = 0 or (p.principalpaidmtd is null and p.interestpaidmtd is null) then null
           else (coalesce(p.principalpaidmtd, 0) + coalesce(p.interestpaidmtd, 0)) / p.schedule_pandi_daily
           end as pandi_paid_times_daily
from r
left join p on r.loanid = p.loanid
left join p2 on r.loanid = p2.loanid
left join port.basic_data_monthly_loan_common mc
    on r.fctrdt = mc.fctrdt
   and r.loanid = mc.loanid
   and mc.servicer = 'MRC'
left join port.portfunding f on r.loanid = f.loanid;
