-- auto-extracted by tools/freeze_snapshot.py plan
-- source: flow\remit_validation\mrc_validation.py :: mrc_summary_check
-- servicer: mrc
-- remit_date: 2026-04-30
-- placeholders to resolve: mrc_db.fctrdt
-- notes: auto-extracted; resolve `{...}` placeholders before export

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
              and fctrdt = '{mrc_db.fctrdt}';
