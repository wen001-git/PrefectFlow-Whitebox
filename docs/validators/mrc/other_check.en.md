# MRC Advance Info (3rd party / corp / escrow buckets MoM)

**ID**: `mrc/other_check` &nbsp;&nbsp; **Servicer**: `mrc` &nbsp;&nbsp; **Source**: `flow/remit_validation/mrc_validation.py:136`

Bucketed advance amounts at the description+transaction_code level for three advance
categories (non-recoverable corp, recoverable corp, escrow), with prior-month MoM
ratio. Used by ops to investigate unusual movements.

## Business rule

For current and prior fctrdt, run a UNION of three bucketed aggregates:
(1) nonrecovcorpadv: sum(advances + recoveries) from portmrcremit3rdpartyadvances grouped by (description, tran_code);
(2) recovcorpadv: same metric from portmrcremitcorpadvances grouped by (reason, tran_code);
(3) escadv: sum(total_activity) from portmrcremitescrowadvances grouped by (cat, disbursement_code).
Then merge current + prior on (bucket, description, transaction_code) in pandas and compute amt_MoM = amt / amt_1m - 1.

!!! info "Business impact"
    Large MoM swings prompt ops to query unusual transaction codes.

## Produces sheets

- [MRC_Adv_Info](../../sheets/MRC_Adv_Info.md) — Bucketed advance amounts at the description + transaction_code level for three advance
categories (non-recoverable corp, recoverable corp, escrow), with prior-month MoM ratio.


## Source tables

- `mrc.portmrcremit3rdpartyadvances`
- `mrc.portmrcremitcorpadvances`
- `mrc.portmrcremitescrowadvances`

*(Pure-Python validator; no extracted SQL file.)*

**Tags**: `mrc`, `advance_detail`, `pandas_merge`, `stub`