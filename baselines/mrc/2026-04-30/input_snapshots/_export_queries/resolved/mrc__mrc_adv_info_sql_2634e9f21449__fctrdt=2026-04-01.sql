-- TEMPLATE: _export_queries/template/mrc__mrc_adv_info_sql_2634e9f21449.sql
-- BINDINGS: fctrdt=2026-04-01
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

select
            'nonrecovcorpadv' as bucket,
            description,
            tran_code as transaction_code,
            sum(coalesce(advances, 0) + coalesce(recoveries, 0)) as amt
        from mrc.portmrcremit3rdpartyadvances
        where fctrdt = '2026-04-01'
        group by description, tran_code
        union all
        select
            'recovcorpadv' as bucket,
            reason as description,
            tran_code as transaction_code,
            sum(coalesce(advances, 0) + coalesce(recoveries, 0)) as amt
        from mrc.portmrcremitcorpadvances
        where fctrdt = '2026-04-01'
        group by reason, tran_code
        union all
        select
            'escadv' as bucket,
            cat as description,
            disbursement_code as transaction_code,
            sum(total_activity) as amt
        from mrc.portmrcremitescrowadvances
        where fctrdt = '2026-04-01'
        group by cat, disbursement_code;
