-- TEMPLATE: _export_queries/template/mrc__mrc_summary_check_e943649b57cd.sql
-- BINDINGS: mrc_db.fctrdt=2026-05-01
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

select
                sum(principalreceived) as principalreceived,
                sum(interestreceived) as interestreceived,
                sum(escrowadv_chg) as escrowadv_chg,
                sum(corpadvrec_chg) as corpadvrec_chg,
                sum(corpadvnonrec_chg) as corpadvnonrec_chg,
                sum(corpadvtotal_chg) as corpadvtotal_chg,
                sum(servicefee) as servicefee,
                sum(otherfees) as otherfees,
                sum(servicefee + otherfees) as totalservicefee,
                sum(subremit) as subremit,
                sum(totremit) as totremit,
                sum(prevbal) as beginningbalance,
                sum(balance) as endingbalance
            from port.portmonth
            where servicer = 'MRC'
              and fctrdt = '2026-05-01';
