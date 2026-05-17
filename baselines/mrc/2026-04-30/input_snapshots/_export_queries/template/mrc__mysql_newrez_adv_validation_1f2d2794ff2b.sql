-- auto-extracted by tools/freeze_snapshot.py plan (v2.1)
-- source: flow/remit_validation/servicer_validation_with_portdaily.py :: mysql_newrez_adv_validation (lines 257–310)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string-noexpr
-- placeholders to resolve: (none)
-- notes: non-MRC (other servicer SQL in shared module); module-level template (used via .replace() in caller)

select p1.loanid, p1.svcloanid as shellpoint_ln, f.dealid,
p1.delq_status as delq_status
, coalesce(p1.escrow_advance_balance, 0) as escrowadv_prev_daily
, coalesce(p2.escrow_advance_balance, 0) as escrowadv_curr_daily
, coalesce(p2.escrow_advance_balance, 0) - coalesce(p1.escrow_advance_balance, 0) as escrowadv_chg_daily
, -1 * coalesce(p1.reccorpadvance, 0) as reccorpadvance_prev_daily
, -1 * coalesce(p2.reccorpadvance, 0) as reccorpadvance_curr_daily
, -1 * coalesce(p1.nonrecovadvance, 0) as thirdpartyrecovadv_prev_daily
, -1 * coalesce(p2.nonrecovadvance, 0) as thirdpartyrecovadv_curr_daily
, -1 * coalesce(p1.reccorpadvance, 0) -1 * coalesce(p1.nonrecovadvance, 0) as totalcorpadv_prev_daily
, -1 * coalesce(p2.reccorpadvance, 0) -1 * coalesce(p2.nonrecovadvance, 0) as  totalcorpadv_curr_daily
, -1 * coalesce(p2.reccorpadvance, 0) + 1 * coalesce(p1.reccorpadvance, 0) as reccorpadvance_chg_daily
, -1 * coalesce(p2.nonrecovadvance, 0) + 1 * coalesce(p1.nonrecovadvance, 0) as thirdpartyrecovadv_chg_daily
, (-1 * coalesce(p2.reccorpadvance, 0) -1 * coalesce(p2.nonrecovadvance, 0)) - (-1 * coalesce(p1.reccorpadvance, 0) -1 * coalesce(p1.nonrecovadvance, 0)) as totalcorpadv_chg_daily
, r.netchange as reccorpadvance_remit
, n.netchange as nonrecovadvance_remit
, e.netchange as escadv_remit
, r.netchange + n.netchange as totalcorpadvance_remit
, (coalesce(p2.escrow_advance_balance, 0) - coalesce(p1.escrow_advance_balance, 0)) + e.netchange as escadv_diff_remitvsdaily
, (-1 * coalesce(p2.nonrecovadvance, 0) + 1 * coalesce(p1.nonrecovadvance, 0)) + n.netchange as nonrecovcorpadv_diff_remitvsdaily
,e2.int_on_escrow as int_on_escrow
, (-1 * coalesce(p2.reccorpadvance, 0) + 1 * coalesce(p1.reccorpadvance, 0)) + r.netchange as recovcorpadv_diff_remitvsdaily
, (-1 * coalesce(p2.reccorpadvance, 0) -1 * coalesce(p2.nonrecovadvance, 0)) - (-1 * coalesce(p1.reccorpadvance, 0) -1 * coalesce(p1.nonrecovadvance, 0)) + (r.netchange + n.netchange) as totalcorpadv_diff_remitvsdaily
from port.basic_data_daily_loan_common p1
inner join
    port.basic_data_daily_loan_common p2
on
    p1.loanid = p2.loanid
inner join
    newrez.portnewrezremitrecovcorpadvchange r
on
    p1.loanid = r.loanid
inner join
    newrez.portnewrezremitnonrecovcorpadvchange n
on
    p1.loanid = n.loanid
inner join
    newrez.portnewrezremitescadvchange e
on
    p1.loanid = e.loanid
left join (select loanid, sum(transactionamt) as int_on_escrow from newrez.portnewrezremitnonrecovcorpadvdetail where fctrdt = 'input_fctrdt' and description = 'Int on Escrow Pmt' group by loanid) e2
on p1.loanid = e2.loanid
left join
    port.portfunding f
on
    p1.loanid = f.loanid
where
    r.fctrdt = 'input_fctrdt'
and n.fctrdt = r.fctrdt
and e.fctrdt = r.fctrdt
and p1.asofdate = 'input_pre_month_end'
and p2.asofdate = 'input_curr_month_end';
