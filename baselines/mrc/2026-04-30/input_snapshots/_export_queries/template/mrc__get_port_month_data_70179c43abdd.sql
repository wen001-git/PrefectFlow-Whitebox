-- auto-extracted by tools/freeze_snapshot.py plan (v2.0)
-- source: flow/remit_validation/carrington_db.py :: get_port_month_data (lines 35–47)
-- servicer: mrc  flag: MRC-relevant
-- remit_date: 2026-04-30
-- pattern: f-string
-- placeholders to resolve: service
-- placeholder hints:
--   service: servicer name string, e.g. 'MRC'
-- notes: resolve 1 placeholder(s) before export

select
                            case
                                when b.loanid is null then a.servicer
                                else 'SLS'
                            end as data_servicer,
                            a.*
                        from port.portmonth a
                            left join
                        (select loanid from port.portmonth where servicer = 'SLS' and fctrdt = '2024-07-01') b
                        on a.loanid = b.loanid
                        where a.servicer = '{service}';
