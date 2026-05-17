-- auto-extracted by tools/freeze_snapshot.py plan
-- source: flow\remit_validation\mrc_validation.py :: _mrc_adv_info_sql
-- servicer: mrc
-- remit_date: 2026-04-30
-- placeholders to resolve: fctrdt
-- notes: auto-extracted; resolve `{...}` placeholders before export

select
            'nonrecovcorpadv' as bucket,
            description,
            tran_code as transaction_code,
            sum(coalesce(advances, 0) + coalesce(recoveries, 0)) as amt
        from mrc.portmrcremit3rdpartyadvances
        where fctrdt = '{fctrdt}'
        group by description, tran_code
        union all
        select
            'recovcorpadv' as bucket,
            reason as description,
            tran_code as transaction_code,
            sum(coalesce(advances, 0) + coalesce(recoveries, 0)) as amt
        from mrc.portmrcremitcorpadvances
        where fctrdt = '{fctrdt}'
        group by reason, tran_code
        union all
        select
            'escadv' as bucket,
            cat as description,
            disbursement_code as transaction_code,
            sum(total_activity) as amt
        from mrc.portmrcremitescrowadvances
        where fctrdt = '{fctrdt}'
        group by cat, disbursement_code;
