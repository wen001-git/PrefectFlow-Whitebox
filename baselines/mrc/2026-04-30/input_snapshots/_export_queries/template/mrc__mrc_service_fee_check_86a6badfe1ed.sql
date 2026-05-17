-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/mrc_validation.py :: mrc_service_fee_check (lines 79–96)
-- servicer: mrc  flag: MRC-relevant
-- remit_date: 2026-04-30
-- pattern: f-string
-- placeholders to resolve: mrc_db.fctrdt
-- placeholder hints:
--   mrc_db.fctrdt: factor-date (YYYY-MM-01) for remit cycle, e.g. '2026-05-01'
-- notes: resolve 1 placeholder(s) before export

select
                r.fctrdt,
                r.loanid,
                r.mrc_ln,
                coalesce(p.dealid, f.dealid) as dealid,
                r.total_accrued_earned_servicing_fees as servicefee_remit_raw,
                p.servicefee as servicefee_portmonth,
                r.total_accrued_earned_servicing_fees - p.servicefee as servicefee_diff
            from mrc.portmrcremitloanlevelrecap r
            left join port.portmonth p
                on r.fctrdt = p.fctrdt
               and r.loanid = p.loanid
               and p.servicer = 'MRC'
            left join port.portfunding f
                on r.loanid = f.loanid
            where r.fctrdt = '{mrc_db.fctrdt}';
