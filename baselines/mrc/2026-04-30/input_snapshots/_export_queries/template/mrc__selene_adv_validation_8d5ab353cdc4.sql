-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: selene_adv_validation (lines 450–508)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

with r as (
    select *
    from port.portmonth
    where servicer = 'Selene'
      and fctrdt = 'input_fctrdt'
),
p1 as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = 'input_pre_month_end'
      and servicer = 'Selene'
),
p2 as (
    select *
    from port.basic_data_daily_loan_common
    where asofdate = 'input_curr_month_end'
      and servicer = 'Selene'
)
select r.loanid,
       r.svcloanid as selene_ln,
       coalesce(r.dealid, f.dealid) as dealid,
       p1.delq_status as delq_status,
       coalesce(p1.escrow_advance_balance, 0) as escrowadv_prev_daily,
       coalesce(p2.escrow_advance_balance, 0) as escrowadv_curr_daily,
       escrowadv_curr_daily - escrowadv_prev_daily as escrowadv_chg_daily,
       coalesce(p1.reccorpadvance, 0) as reccorpadvance_prev_daily,
       coalesce(p2.reccorpadvance, 0) as reccorpadvance_curr_daily,
       coalesce(p1.nonrecovadvance, 0) as nonrecovcorpadv_prev_daily,
       coalesce(p2.nonrecovadvance, 0) as nonrecovcorpadv_curr_daily,
       reccorpadvance_prev_daily + nonrecovcorpadv_prev_daily as totalcorpadv_prev_daily,
       reccorpadvance_curr_daily + nonrecovcorpadv_curr_daily as totalcorpadv_curr_daily,
       reccorpadvance_curr_daily - reccorpadvance_prev_daily as reccorpadvance_chg_daily,
       case
           when p1.nonrecovadvance is null and p2.nonrecovadvance is null then null
           else nonrecovcorpadv_curr_daily - nonrecovcorpadv_prev_daily
           end as nonrecovcorpadv_chg_daily,
       totalcorpadv_curr_daily - totalcorpadv_prev_daily as totalcorpadv_chg_daily,
       coalesce(r.corpadvrec_chg, 0) as reccorpadvance_remit,
       coalesce(r.corpadvnonrec_chg, 0) as nonrecovadvance_remit,
       coalesce(r.escrowadv_chg, 0) as escadv_remit,
       coalesce(r.corpadvtotal_chg, coalesce(r.corpadvrec_chg, 0) + coalesce(r.corpadvnonrec_chg, 0)) as totalcorpadvance_remit,
       escrowadv_chg_daily + escadv_remit as escadv_diff_remitvsdaily,
       case
           when nonrecovcorpadv_chg_daily is null then null
           else nonrecovcorpadv_chg_daily + nonrecovadvance_remit
           end as nonrecovcorpadv_diff_remitvsdaily,
       reccorpadvance_chg_daily + reccorpadvance_remit as recovcorpadv_diff_remitvsdaily,
       case
           when nonrecovcorpadv_chg_daily is null then null
           else totalcorpadv_chg_daily + totalcorpadvance_remit
           end as totalcorpadv_diff_remitvsdaily,
       coalesce(p1.escrowbalance, 0) as escrow_balance_prev,
       coalesce(p2.escrowbalance, 0) as escrow_balance_curr
from r
left join p1 on r.loanid = p1.loanid
left join p2 on r.loanid = p2.loanid
left join port.portfunding f on r.loanid = f.loanid;
