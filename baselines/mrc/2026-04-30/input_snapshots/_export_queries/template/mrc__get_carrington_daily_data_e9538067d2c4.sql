-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/carrington_db.py :: get_carrington_daily_data (lines 107–107)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string
-- placeholders to resolve: table, str(query_date)
-- placeholder hints:
--   table: Redshift table name resolved at runtime
--   str(query_date): as-of date for daily snapshot (string form)
-- notes: non-MRC (other servicer SQL in shared module); resolve 2 placeholder(s) before export

select * from {table} where snap_shot_date = '{str(query_date)}'
