-- TEMPLATE: _export_queries/template/mrc__mrc_service_fee_check_86a6badfe1ed.sql
-- BINDINGS: mrc_db.fctrdt=2026-05-01
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

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
            where r.fctrdt = '2026-05-01';
