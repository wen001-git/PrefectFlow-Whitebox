# MRC servicer — scope

> Extracted from the read-only source repo on 2026-05-16.
> Sources: `flow/remit_validation/mrc_validation.py`, `flow/remit_validation/servicer_validation_with_portdaily.py`, `flow/remit_validation/remit_validation.py`, `util/gen_remit_validation_report.py`.

## Validators (5)

| # | Validator (task name) | Produces sheet | Source citation | # cols | Mechanism |
|---|---|---|---|---|---|
| 1 | `mrc_summary_check` | **MRC_Summary_check** | `flow/remit_validation/mrc_validation.py:8-36` | 14 | Aggregate sums from `port.portmonth` for `servicer='MRC'`, one row. |
| 2 | `mrc_check_general_info` | **MRC_General_Check** | `flow/remit_validation/mrc_validation.py:57-72` + SQL at `servicer_validation_with_portdaily.py:635-701` | ~30 | Loan-level join of `portmonth` (remit) vs `basic_data_daily_loan_common` (daily) with `*_diff_remitvsdaily` columns highlighted on diff. |
| 3 | `mrc_check_adv_balance` | **MRC_Advance_Check** | `flow/remit_validation/mrc_validation.py:39-54` + SQL at `servicer_validation_with_portdaily.py:583-632` | ~25 | Loan-level advance-balance reconciliation (escrow / recov / non-recov corp adv) remit vs daily. |
| 4 | `mrc_service_fee_check` | **MRC_ServiceFee_Check** | `flow/remit_validation/mrc_validation.py:75-102` | 9 | Loan-level service-fee reconciliation: `portmrcremitloanlevelrecap.total_accrued_earned_servicing_fees` vs `portmonth.servicefee`. |
| 5 | `mrc_other_check` | **MRC_Adv_Info** | `flow/remit_validation/mrc_validation.py:136-158` (+ helper `_mrc_adv_info_sql` at 105-133) | 8 | Bucketed advance amounts (`nonrecovcorpadv` / `recovcorpadv` / `escadv`) for current month merged with prior-month for MoM ratio (pandas merge). |

(Column counts from `util/gen_remit_validation_report.py:1180-1293` helpers — `_summary_columns`, `_general_columns("mrc_ln")`, `_advance_columns("mrc_ln")`, `_service_fee_columns("mrc_ln")`, `_adv_info_columns`.)

## Output sheet declarations

Defined as a single `dict.update` block in `util/gen_remit_validation_report.py:1327-1357`:

- `MRC_Summary_check` — `_summary_columns()`
- `MRC_General_Check` — `_general_columns("mrc_ln")` + diff highlight columns: `intrate_diff_remitvsdaily`, `nextduedate_diff_remitvsdaily`, `begbal_diff_remitvsdaily`, `endbal_diff_remitvsdaily`, `deferredprincipal_diff_remitvsdaily`, `deferredint_diff_remitvsdaily`, `pandi_schedule_diff_remitvsdaily`
- `MRC_Advance_Check` — `_advance_columns("mrc_ln")` + diff highlight columns: `escadv_diff_remitvsdaily`, `recovcorpadv_diff_remitvsdaily`, `nonrecovcorpadv_diff_remitvsdaily`, `totalcorpadv_diff_remitvsdaily`
- `MRC_ServiceFee_Check` — `_service_fee_columns("mrc_ln")` + diff highlight: `servicefee_diff`
- `MRC_Adv_Info` — `_adv_info_columns()`

## Source tables (Redshift)

| Schema.Table | Used by validator |
|---|---|
| `port.portmonth` | v1, v2, v3, v4 (the remit master table for MRC) |
| `port.basic_data_daily_loan_common` | v2, v3 (the daily snapshot, joined for "remit vs daily" diffs) |
| `port.basic_data_monthly_loan_common` | v2 (scheduled P&I lookup) |
| `port.portfunding` | v2, v3, v4 (dealid fallback) |
| `mrc.portmrcremitloanlevelrecap` | v4 (MRC-specific accrued service fee) |
| `mrc.portmrcremit3rdpartyadvances` | v5 (3rd-party advances bucket) |
| `mrc.portmrcremitcorpadvances` | v5 (recoverable corp advances bucket) |
| `mrc.portmrcremitescrowadvances` | v5 (escrow advances bucket) |

## Flow wiring (orchestration in source)

In `flow/remit_validation/remit_validation.py:134-144` the 5 task outputs are stored into a global `VALIDATION_TABLE_MAP`:

```python
VALIDATION_TABLE_MAP['mrc_summary_check']   = mrc_summary_df
VALIDATION_TABLE_MAP['mrc_general_check']   = mrc_general_df
VALIDATION_TABLE_MAP['mrc_adv_check']       = mrc_adv_df
VALIDATION_TABLE_MAP['mrc_service_fee_check'] = mrc_service_fee_df
VALIDATION_TABLE_MAP['mrc_adv_info']        = mrc_adv_info_df
```

The keys above map to writer sheet names via `util/gen_remit_validation_report.py`'s `sheet_setting` registry (line 1327+).

## Notes / observations

- **v1 (Summary)** is a single-row aggregate — simplest validator; good first target.
- **v5 (Adv_Info)** is the only validator that uses pandas merge (current month vs prior month) outside SQL — needs Python parity, not just SQL parity. Also pulls `_mrc_adv_info_sql` twice (current `fctrdt` + prior `fctrdt_1m`).
- **v2 and v3** share a similar structure (CTE `r`/`p`/`p2` over portmonth + daily snapshots) and reference the same upstream tables — they will share most lineage extraction work.
- **No SLS-style empty-data bug** observed in MRC code path (no `params=None` style issue).
- `mrc_ln` is the MRC servicer loan number; corresponds to `svcloanid` column in `port.portmonth`.

## Implementation order (recommended)

1. **v1 (Summary)** — smallest, single-row, single-table → builds confidence in YAML + harness loop end-to-end.
2. **v4 (ServiceFee)** — small (9 cols), self-contained SQL in `mrc_validation.py` itself.
3. **v5 (Adv_Info)** — adds the Python-merge wrinkle; isolates that complexity early.
4. **v2 (General)** — largest SQL (~30 cols), the heaviest sqlglot stress test.
5. **v3 (Advance)** — same shape as v2, should be fastest once v2 is done.
