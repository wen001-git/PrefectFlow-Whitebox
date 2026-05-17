-- TEMPLATE: _export_queries/template/mrc__get_port_month_data_70179c43abdd.sql
-- BINDINGS: service=MRC
-- GENERATED: 2026-05-17
-- REVIEW BEFORE RUNNING

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
                        where a.servicer = 'MRC';
