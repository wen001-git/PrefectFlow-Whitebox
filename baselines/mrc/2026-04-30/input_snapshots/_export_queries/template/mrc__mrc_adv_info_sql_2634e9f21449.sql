-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/mrc_validation.py :: _mrc_adv_info_sql (lines 106–133)
-- servicer: mrc  flag: MRC-relevant
-- remit_date: 2026-04-30
-- pattern: f-string
-- placeholders to resolve: fctrdt
-- placeholder hints:
--   fctrdt: factor-date parameter (YYYY-MM-01), e.g. '2026-05-01'
-- notes: resolve 3 placeholder(s) before export

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
