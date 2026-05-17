-- auto-extracted by tools/freeze_snapshot.py plan (v2.1)
-- source: flow/remit_validation/carrington_db.py :: get_carrington_trans (lines 152–152)
-- servicer: mrc  flag: non-MRC (other servicer)
-- remit_date: 2026-04-30
-- pattern: f-string
-- placeholders to resolve: table, str(self.fctrdt)
-- placeholder hints:
--   table: Redshift table name resolved at runtime
--   str(self.fctrdt): factor-date for this cycle (string form)
-- notes: non-MRC (other servicer SQL in shared module); resolve 2 placeholder(s) before export

select * from {table} where dataasofdate = '{str(self.fctrdt)}';
