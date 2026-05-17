# Validation Report Logic Doc — Table of Contents (Stage 1, deliverable #1)

> This TOC is the **gating deliverable for Stage 1**. It enumerates every chapter,
> every servicer, every sheet, and the depth-of-coverage we will write for each,
> so the user can approve scope before any chapter is written. Only after the user
> approves this TOC will chapters `1.1 → 1.2 → 1.3 → 1.4` be drafted in order.
>
> **No new-system design, no technology selection, and no new code appears in this
> TOC.** All content is strictly reverse-engineered from the existing source under
> `C:\Users\jli\MyData\Copilot\PrefectFlow`.

中文版见 / Chinese version: `toc.zh.md` (use the language switcher in the site header)

---

## Source-of-truth references

Every servicer / sheet listed below is extracted directly from the source files
below and is traceable line-by-line.

- Entry flow: `flow/remit_validation/remit_validation.py` (180 lines)
  - The `@flow remit_validation_check` function (lines 66-177) invokes 7 per-servicer validators plus 8 scattered cross-servicer validators in a fixed order, stuffs each result into `VALIDATION_TABLE_MAP`, then calls `gen_remit_report` to produce the XLSX.
- Sheet registration: `util/gen_remit_validation_report.py`
  - The top-level `setting["sheet_setting"]` dict (lines 87-1162) registers 30 sheets covering SLS, Carrington, Shellpoint, Arvest, CC5 and scattered.
  - The `setting["sheet_setting"].update({...})` block (lines 1296-1357) appends 5 Selene + 5 MRC sheets for a final total of 40.
  - Column-template helpers: `_summary_columns` / `_general_columns` / `_advance_columns` / `_service_fee_columns` / `_adv_info_columns` (lines 1180-1294).
- Per-servicer validator modules: `flow/remit_validation/<servicer>_validation.py` and matching `_db.py`.
- Cross-servicer validators: `flow/remit_validation/scattered_validation.py`.
- Shared SQL blocks: `flow/remit_validation/servicer_validation_with_portdaily.py`.

---

## Validation Report at a glance (40 sheets in the final XLSX)

Source: `gen_remit_report` receives 40 DataFrames in `remit_validation.py:165-175` and writes them sequentially into the sheets listed below.

| # | Sheet | Owner | Source DataFrame | Producing function |
|---|---|---|---|---|
| 1 | `SLS_Summary_check`           | SLS        | `None` (not wired) | `sls_summary_check` (defined, not invoked) |
| 2 | `SLS_Advance_Check`           | SLS        | `None`                       | `sls_validation_check`        |
| 3 | `SLS_General_Check`           | SLS        | `None`                       | `sls_general_check`           |
| 4 | `SLS_ServiceFee_Check`        | SLS        | `None`                       | `sls_check_service_fee`       |
| 5 | `SLS_Other_Check`             | SLS        | `None`                       | `sls_other_fee`               |
| 6 | `Carrington_Summary_check`    | Carrington | `carrington_summary_df`      | `carrington_summary_check`    |
| 7 | `Carrington_General_Check`    | Carrington | `carrington_general_df`      | `carrington_general_info_check` |
| 8 | `Carrington_Advance_Check`    | Carrington | `carrington_adv_df`          | `carrington_new_adv_check`    |
| 9 | `Carrington_ServiceFee_Check` | Carrington | `carrington_service_fee`     | `carrington_service_fee_check`|
| 10 | `Carrington_Adv_Info`        | Carrington | `carrington_adv_info` (2nd return) | `carrington_other_check` |
| 11 | `Carrington_Trans_Info`      | Carrington | `trans_df` (1st return)            | `carrington_other_check` |
| 12 | `Shellpoint_Summary_check`   | Shellpoint | `shellpoint_summary_df`      | `shellpoint_summary_check`    |
| 13 | `Shellpoint_General_Check`   | Shellpoint | `s_general_df`               | `shellpoint_check_general_info` |
| 14 | `Shellpoint_Advance_Check`   | Shellpoint | `s_adv_df`                   | `shellpoint_check_avd_balance` |
| 15 | `Shellpoint_ServiceFee_Check`| Shellpoint | `shellpoint_service_fee`     | `shellpoint_service_fee_check`|
| 16 | `Shellpoint_Adv_Info`        | Shellpoint | `shellpoint_adv_info`        | `shellpoint_other_check`      |
| 17 | `Arvest_Sum_remit`           | Arvest     | `sum_remit_df`               | `arvest_get_sub_and_tot_remit`|
| 18 | `Arvest_Bal_Chg_check`       | Arvest     | `arvest_bal_chg_df`          | `arvest_compare_bal_chg`      |
| 19 | `Arvest_PandI_check`         | Arvest     | `arvest_pandi_compare_df`    | `arvest_pandi_info_check`     |
| 20 | `Arvest_ServiceFee_check`    | Arvest     | `arvest_service_fee_df`      | `arvest_service_fee_check`    |
| 21 | `Cc5_ServiceFee_check`       | CC5        | `cc5_service_fee_check_df`   | `cc5_service_fee_check`       |
| 22 | `Cc5_bal_check`              | CC5        | `cc5_bal_check_df`           | `cc5_principal_bal_check`     |
| 23 | `Month_vs_Funding`           | Scattered  | `month_vs_funding`           | `adv_month_vs_funding`        |
| 24 | `PandI_vs_NextDueDate`       | Scattered  | `pandi_vs_nextdue_date`      | `check_pandi_nextduedate_logic` |
| 25 | `Service Fee All`            | Scattered  | `service_fee_all`            | `all_servicer_fee_check`      |
| 26 | `Paid-off Loans Check`       | Scattered  | `paid_off_loans`             | `check_paid_off_loans`        |
| 27 | `Mod_loans_info`             | Scattered  | `modi_loan_info`             | `check_modi_loan_info`        |
| 28 | `Loan_Scale_info`            | Scattered  | `loans_scale_info`           | `check_loans_scale_info`      |
| 29 | `PandI_check`                | Scattered  | `pandi_compare_df`           | `compare_pandi`               |
| 30 | `Paidoff_deffer_check`       | Scattered  | `paidoff_loans_deffer_df`    | `check_paidoff_loans_deffer`  |
| 31 | `Selene_Summary_check`       | Selene     | `selene_summary_df`          | `selene_summary_check`        |
| 32 | `Selene_General_Check`       | Selene     | `selene_general_df`          | `selene_check_general_info`   |
| 33 | `Selene_Advance_Check`       | Selene     | `selene_adv_df`              | `selene_check_adv_balance`    |
| 34 | `Selene_ServiceFee_Check`    | Selene     | `selene_service_fee_df`      | `selene_service_fee_check`    |
| 35 | `Selene_Adv_Info`            | Selene     | `selene_adv_info_df`         | `selene_other_check`          |
| 36 | `MRC_Summary_check`          | MRC        | `mrc_summary_df`             | `mrc_summary_check`           |
| 37 | `MRC_General_Check`          | MRC        | `mrc_general_df`             | `mrc_check_general_info`      |
| 38 | `MRC_Advance_Check`          | MRC        | `mrc_adv_df`                 | `mrc_check_adv_balance`       |
| 39 | `MRC_ServiceFee_Check`       | MRC        | `mrc_service_fee_df`         | `mrc_service_fee_check`       |
| 40 | `MRC_Adv_Info`               | MRC        | `mrc_adv_info_df`            | `mrc_other_check`             |

⚠️ **SLS status note (verified against `remit_validation.py`)**: The flow body
at lines 66-177 contains **zero SLS validator invocations**, even though
`sls_validation.py` defines 5 validator functions that are imported at lines
27-29. When `gen_remit_report` is called (line 166) the 5 SLS slots are passed
as `None`, which is why the SLS sheets in the 2026-04-30 gold XLSX contain only
header rows. Chapter `1.2.7 SLS` will record this explicitly and contrast the
intended SLS validator behavior with the gap in the current flow.

---

## Document outline (full chapter list for Stage 1)

Per user prompt #19, Stage 1 documentation covers four dimensions. All content
is reverse-engineered from existing source code; **no new-system concepts and
no technology recommendations are introduced**.

### 1.1 `overall-flow.en.md` — Overall generation flow

Sub-sections:

- 1.1.1 Entry point: the `@flow remit_validation_check` decorator, the 4 parameters (`remit_date` / `email` / `to_new_redshift` / `to_mysql`), their semantics, and how `remit_date=None` is back-computed to "last day of previous month".
- 1.1.2 Data-source landscape: per-servicer raw schemas on Redshift, the unified servicer tables, and the portfolio-daily tables.
- 1.1.3 The full `VALIDATION_TABLE_MAP` dictionary — all 30 keys, the meaning of each, and the exact step in the flow at which each key is populated.
- 1.1.4 Inventory of relevant Python files, organized by call graph, each annotated with its role.
- 1.1.5 Inventory of relevant SQL files / SQL blocks (e.g. `servicer_validation_with_portdaily.py`).
- 1.1.6 Final XLSX output: path-construction rule (`VALIDATION_REPORT_ROUTE + date_path + ...`), the physical write order of the 40 sheets, and the writer pipeline inside `gen_remit_report`.
- 1.1.7 Mermaid sequence diagram covering flow startup → DB classes → validators → `VALIDATION_TABLE_MAP` writes → XLSX persistence.

### 1.2 Per-servicer chapters (in true flow invocation order)

Each chapter uses the same four-dimensional structure:

- **(a) Servicer overview** — DB class, validator module, input arguments, the list of Redshift tables consumed, and which sheets this servicer produces.
- **(b) Per-sheet generation logic** — for **every** sheet: sheet name, producing function / SQL / DataFrame, data sources, join keys, filter conditions, group-by logic, computed fields, validation rules, and pass / fail / exception classification.
- **(c) Per-field calculation logic** — for **every** output column: source table / source field, transformation logic, calculation formula, business meaning, known edge cases.
- **(d) Servicer-local dataflow branch** — Mermaid lineage diagram: raw vendor → raw schema → Redshift unified → validation query → this servicer's sheets.

Chapter ordering follows the true call order in `remit_validation_check`:

- 1.2.1 **Carrington** (6 sheets: Summary / General / Advance / ServiceFee / Adv_Info / Trans_Info)
  - Source: `carrington_validation.py` + `carrington_db.py`; 5 validators (note `carrington_other_check` returns a 2-tuple → 2 sheets).
- 1.2.2 **Shellpoint** (5 sheets: Summary / General / Advance / ServiceFee / Adv_Info)
  - Source: `shellpoint_validation.py` + `shellpoint_db.py`; 5 validators.
- 1.2.3 **Arvest** (4 sheets: Sum_remit / Bal_Chg_check / PandI_check / ServiceFee_check)
  - Source: `arvest_validation.py` + `arvest_db.py`; 4 validators.
- 1.2.4 **CC5** (2 sheets: ServiceFee_check / bal_check)
  - Source: `cc5_validation.py` + `cc5_db.py`; 2 validators.
- 1.2.5 **Selene** (5 sheets: Summary / General / Advance / ServiceFee / Adv_Info)
  - Source: `selene_validation.py` + `selene_db.py`; 5 validators.
- 1.2.6 **MRC** (5 sheets: Summary / General / Advance / ServiceFee / Adv_Info)
  - Source: `mrc_validation.py` + `mrc_db.py`; 5 validators.
- 1.2.7 **SLS** (5 sheets, currently empty)
  - Source: `sls_validation.py` + `sls_db.py`; 5 validators **defined but not invoked from the flow**.
  - This chapter must faithfully document: intended behavior of the 5 SLS validators, the fact that `gen_remit_report` receives 5 `None` placeholders, the resulting empty-sheet outputs, and any historical rationale recoverable from git log / inline comments.

### 1.3 Cross-servicer chapter

- 1.3.1 **Scattered cross-servicer validators** (8 sheets)
  - Source: `scattered_validation.py`
  - 8 validators: `adv_month_vs_funding / check_pandi_nextduedate_logic / all_servicer_fee_check / check_paid_off_loans / check_modi_loan_info / check_loans_scale_info / compare_pandi / check_paidoff_loans_deffer`
  - Uses the same four-dimensional structure (overview + per-sheet + per-field + dataflow).

### 1.4 `dataflow.en.md` — Cross-servicer dataflow

- 1.4.1 Raw vendor file → raw schema table lineage: this section only enumerates which raw schema tables belong to which servicer; the upstream ETL is treated as black-box per user decision.
- 1.4.2 Raw schema table → Redshift unified table (portfolio-daily and `*_ln` aggregates) — the unification rules.
- 1.4.3 Unified table → validation query → per-sheet column-level lineage, summarized in a single Mermaid diagram.
- 1.4.4 Cross-servicer flows (e.g. `Service Fee All` reading multiple servicers' intermediate tables).
- 1.4.5 An overall dataflow diagram of the entire Validation Report.

### 1.5 User walk-through (gate — only an explicit user approval marks this done)

- 1.5.1 User reads through chapters 1.1 – 1.4 via the mkdocs site or directly in markdown.
- 1.5.2 User records walk-through feedback in `decisions.md` (coverage / accuracy / business readability).
- 1.5.3 Only after the user writes "stage 1 approved" does Stage 2 unlock.

---

## Explicitly out of scope for this TOC

- ❌ No discussion of new-system features, architecture, or technology selection (no FastAPI / Streamlit / Dagster / DBT etc.).
- ❌ No new Python or SQL code.
- ❌ No rewrite of existing validators.
- ❌ No snapshot / diff harness work (those tools are frozen and not used in Stage 1).
- ❌ The PrefectFlow source repo remains read-only.

Stage 2 (feature list / SRS / pages / data model / API / dev plan / test plan /
phased impl) **only** unlocks after the user approves the Stage 1 walk-through
at step 1.5.

---

## Open items awaiting user decision

Please respond on these before approving the TOC (defaults shown):

1. Default order is 1.2.1 → 1.2.7. Want it changed (e.g. promote MRC to first so we can validate the chapter template on it)?
2. Default columns per field are source / transform / formula / business meaning / edge cases. Add anything (sample values, upstream raw-field name, NULL behavior)?
3. Bilingual format: ✅ Confirmed — separate `.zh.md` / `.en.md` files per chapter.
4. Sheet names containing spaces (`Service Fee All` / `Paid-off Loans Check`): keep the original names (recommended for fidelity) or alias them to underscored forms inside the docs?
