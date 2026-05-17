-- auto-extracted by tools/freeze_snapshot.py plan (v2.1)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: mysql_carrington_adv_validation (lines 52–99)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

select
p1.loanid, p1.svcloanid as carrington_ln_number, f.dealid
, p1.escrow_advance_balance  as escrow_advance_prev
, p2.escrow_advance_balance as escrow_advance_curr
, p1.nonrecovadvance as nonrecovcorpadv_prev
, p2.nonrecovadvance as nonrecovcorpadv_curr
, p1.reccorpadvance as borrower_recoverable_advance_balance_prev
, p2.reccorpadvance as borrower_recoverable_advance_balance_curr
, p2.nonrecovadvance - p1.nonrecovadvance as nonrecovcorpadv_chg_daily
, p2.reccorpadvance - p1.reccorpadvance as recovcorpadv_chg_daily
, p2.escrow_advance_balance - p1.escrow_advance_balance as escadv_chg_daily
, coalesce(tmp.corpadvnonrec_chg , 0) as nonrecovcorpadv_chg_remit
, coalesce(tmp.corpadvrec_chg, 0) as recovcorpadv_chg_remit
, coalesce(tmp.escrow_chg, 0) as escadv_chg_remit
, coalesce(tmp.corpadvnonrec_chg , 0) - (p2.nonrecovadvance - p1.nonrecovadvance) as nonrecovcorpadv_diff
, e2.int_on_escrow as int_on_escrow
, coalesce(tmp.corpadvrec_chg, 0) - (p2.reccorpadvance - p1.reccorpadvance) as recovcorpadv_diff
, coalesce(tmp.escrow_chg, 0) - (p2.escrow_advance_balance - p1.escrow_advance_balance) as escrowadv_diff_remitvsdaily
, p1.escrowbalance as escrow_balance_prev
, p2.escrowbalance as escrow_balance_curr
, p1.delq_status as delq_status
from
(select * from port.basic_data_daily_loan_common where asofdate = 'input_pre_month_end' and servicer= 'Carrington') p1
left join
(select * from port.basic_data_daily_loan_common where asofdate = 'input_curr_month_end' and servicer= 'Carrington') p2
on p2.loanid = p1.loanid
left join
(select
fctrdt
, loanid
, sum(case when adv_bucket in ('InvRec', 'ThirdParty') then tran_amount else 0 end) as corpadvnonrec_chg
, sum(case when adv_bucket in ('Corporate', 'DRM') then tran_amount else 0 end) as corpadvrec_chg
, sum(case when adv_bucket in ('Escrow') then tran_amount else 0 end) as escrow_chg
from carrington.portcarringtonremitadv p
where fctrdt = 'input_fctrdt'
group by fctrdt, loanid
) tmp
on p1.loanid  = tmp.loanid
left join (select loanid, sum(interest_on_escrow_paid_to_morgagor) as int_on_escrow from carrington.portcarringtonremitfee 
            where fctrdt = 'input_fctrdt' group by loanid) e2
on p1.loanid = e2.loanid
left join
    port.portfunding f
on
    p1.loanid = f.loanid
;
