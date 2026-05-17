-- TEMPLATE: _export_queries/template/mrc__mrc_adv_validation_0a77567c40d9.sql
-- BINDINGS: input_curr_month_end=2026-04-30, input_fctrdt=2026-05-01, input_pre_month_end=2026-03-31
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

with r as (
    select *
    from port.portmonth
    where servicer = 'MRC'
      and fctrdt = '2026-05-01'
),
p1 as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = '2026-03-31'
      and servicer = 'MRC'
),
p2 as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = '2026-04-30'
      and servicer = 'MRC'
)
select r.loanid,
       r.svcloanid as mrc_ln,
       coalesce(r.dealid, f.dealid) as dealid,
       p1.delq_status as delq_status,
       coalesce(p1.escrow_advance_balance, 0) as escrowadv_prev_daily,
       coalesce(p2.escrow_advance_balance, 0) as escrowadv_curr_daily,
       case when p1.loanid is null or p2.loanid is null then null else escrowadv_curr_daily - escrowadv_prev_daily end as escrowadv_chg_daily,
       coalesce(p1.reccorpadvance, 0) as reccorpadvance_prev_daily,
       coalesce(p2.reccorpadvance, 0) as reccorpadvance_curr_daily,
       coalesce(p1.nonrecovadvance, 0) as nonrecovcorpadv_prev_daily,
       coalesce(p2.nonrecovadvance, 0) as nonrecovcorpadv_curr_daily,
       reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily as totalcorpadv_prev_daily,
       reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily as totalcorpadv_curr_daily,
       case when p1.loanid is null or p2.loanid is null then null else reccorpadvance_curr_daily - reccorpadvance_prev_daily end as reccorpadvance_chg_daily,
       case when p1.loanid is null or p2.loanid is null then null else nonrecovcorpadv_curr_daily - nonrecovcorpadv_prev_daily end as nonrecovcorpadv_chg_daily,
       case when p1.loanid is null or p2.loanid is null then null else totalcorpadv_curr_daily - totalcorpadv_prev_daily end as totalcorpadv_chg_daily,
       coalesce(r.corpadvrec_chg, 0) as reccorpadvance_remit,
       coalesce(r.corpadvnonrec_chg, 0) as nonrecovadvance_remit,
       coalesce(r.escrowadv_chg, 0) as escadv_remit,
       coalesce(r.corpadvtotal_chg, coalesce(r.corpadvrec_chg, 0) + coalesce(r.corpadvnonrec_chg, 0)) as totalcorpadvance_remit,
       escrowadv_chg_daily + escadv_remit as escadv_diff_remitvsdaily,
       nonrecovcorpadv_chg_daily + nonrecovadvance_remit as nonrecovcorpadv_diff_remitvsdaily,
       reccorpadvance_chg_daily + reccorpadvance_remit as recovcorpadv_diff_remitvsdaily,
       totalcorpadv_chg_daily + totalcorpadvance_remit as totalcorpadv_diff_remitvsdaily,
       coalesce(p1.escrowbalance, 0) as escrow_balance_prev,
       coalesce(p2.escrowbalance, 0) as escrow_balance_curr
from r
left join p1 on r.loanid = p1.loanid
left join p2 on r.loanid = p2.loanid
left join port.portfunding f on r.loanid = f.loanid;
