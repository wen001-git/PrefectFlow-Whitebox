# 1.6 Baseline XLSX Behavior / Baseline XLSX 行为

> **Purpose**: Pin down the actual XLSX file produced by `gen_remit_validation_report.py` for `(servicer=MRC, remit_date=2026-04-30)` into a **machine-verifiable, code-reproducible** baseline (baseline): which sheets exist, column order, header style, per-cell `number_format`, highlight overlay, and `±inf` / `NaN` rendering. 1.6 Baseline XLSX Behavior (baseline.en.md) is the **single ultimate acceptance criterion** for the Stage 2 cell-identical rewrite; any deviation between Stage 2 output and this baseline must be explicitly sanctioned in `decisions.md`.
>
> **Audience**: Stage 2 renderer implementers (must reproduce byte-for-cell), cell-identity harness authors, Stage 1 reviewers doing the final walkthrough, QA acceptance signers.
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — initial. Baseline contract reverse-engineered from source (`util/gen_remit_validation_report.py:19-86, 1157-1798` + five helpers and five registry entries `:1180-1356`) and 1.3 Sheet Rendering Layer (sheets.en.md) § 4; lists every render attribute derivable from code + every gap **requiring physical verification** (tagged `[VERIFY]`, to be back-filled once `baselines/mrc/2026-04-30/validation_report.xlsx` lands). |

> **MRC chapter index** (`docs/mrc/`) — full definition in [`_chapter-index.md`](_chapter-index.md)
>
> | # | Title | File | Scope |
> |---|---|---|---|
> | 1.0 | TOC & Scope / 章节地图与范围 | `toc.en.md` | Entry + contracts |
> | 1.1 | Raw Data Layer / 原始数据层 | `rawdata.en.md` | Upstream tables + time anchors |
> | 1.2 | Dataflow Layer / 数据流层 | `dataflow.en.md` | End-to-end pipeline |
> | 1.3 | Sheet Rendering Layer / Sheet 渲染层 | `sheets.en.md` | openpyxl rendering contract |
> | 1.4 | Field Definitions / 字段定义 | `fields.en.md` | Field-level lineage + business meaning |
> | 1.5 | Validation Rules / 验证规则 | `rules.en.md` | Rule catalog |
> | 1.6 | Baseline XLSX Behavior / Baseline XLSX 行为 | `baseline.en.md` | Baseline truth |
> | 1.7 | User Review Gate / 用户走读评审 | (user action) | Stage 2 gate |

---

## 1. Document role

This document is sub-chapter **1.6** of the MRC chapter. It answers exactly one question: **for the frozen `(MRC, 2026-04-30)` (servicer, remit_date) tuple, what does the XLSX file actually produced by `gen_remit_validation_report.py` look like? Which attributes are contracts Stage 2 must reproduce byte-for-cell, and which are openpyxl-default side-effects rather than deliberate design?**

1.6 Baseline XLSX Behavior (baseline.en.md) vs. the preceding 5 chapters:

- 1.3 Sheet Rendering Layer (sheets.en.md) describes the **rendering mechanism** (what the code does); this chapter describes the **rendering output** (what the final XLSX looks like).
- 1.4 Field Definitions (fields.en.md) describes **column lineage** (where each column comes from); this chapter describes the **physical XLSX appearance of each column** (number_format, width, header style).
- 1.5 Validation Rules (rules.en.md) describes **decision rules** (when something counts as an exception); this chapter describes the **visual encoding of an exception in the XLSX** (exact RGB of pink fill / orange font).

This chapter does **not**:

- Restate the rendering pipeline — see 1.3 Sheet Rendering Layer (sheets.en.md) § 3.
- Define business rules — see 1.5 Validation Rules (rules.en.md).
- Describe upstream SQL — see 1.2 Dataflow Layer (dataflow.en.md).

<!-- BUSINESS-PURPOSE-V1 -->
### Business purpose / 业务用途

This chapter is the **closing chapter** of the entire MRC Stage 1 reverse-engineering effort — it materializes "read the code + understand the data flow + catalog the rules" into one final executable contract: "the XLSX looks like this, and Stage 2 must reproduce this". Without a baseline, the Stage 2 rewrite has neither an acceptance yardstick nor a regression-test anchor.

- **Business purpose**: freeze the validation report under the (servicer, remit_date) double-lock into one **canonical truth file** — `baselines/mrc/2026-04-30/validation_report.xlsx` — and write every verifiable attribute (sheet count, column order, header colour, number_format, highlight distribution, ...) as a contract list in 1.6 Baseline XLSX Behavior (baseline.en.md).
- **Business questions answered**:
    - Once the Stage 2 rewrite runs, how do we know it "matches the legacy system"? Answer: cell-identity diff against the baseline (see `stage2-mrc-cell-identity-harness`).
    - When Stage 2 output disagrees with baseline on some cell, is Stage 2 wrong or should baseline itself change? Answer: consult the cell-contract in this chapter first, then decide between "fix Stage 2" or "decision change (decisions.md)".
    - What exactly does openpyxl do for `inf` / `NaN`? If Stage 2 uses a different writer (xlsxwriter, a Rust openpyxl clone, etc.), will it drift on those cells?
- **Population**: one single `(MRC, 2026-04-30)` instance; 5 sheets × actual row counts (row counts depend on the current MRC portfolio; must be measured against the physical baseline).
- **Audience**: Stage 2 renderer implementers, cell-identity harness authors, QA acceptance reviewers, Stage 1 → Stage 2 gate decision makers.
- **Design intent**: close the triangle "code + data + measured XLSX" — any change to one side must leave a trace on the other two.
- **Common failure scenarios**:
    - Stage 2 rewrites with xlsxwriter, default font diverges from openpyxl default → cell-identity diff explodes → triggers the "writer choice" decision in § 7;
    - Upstream SQL renames a column → baseline column order shifts → must (a) sync this chapter §§ 4–6 + (b) re-freeze `baselines/mrc/2026-04-30/`;
    - A month with `amt_1m = 0` triggers `inf` → legacy system shows `1.798e+308` in Excel (openpyxl default), Stage 2 must reproduce or cell-identity fails.
- **Risk / reconciliation motivation**: the baseline is the only objective evidence for Stage 2 acceptance; attributes NOT covered by this chapter = attributes Stage 2 is free to implement = potential sources of future regressions. The § 9 `[VERIFY]` list must therefore be **drained to zero** once the physical baseline lands, before Stage 2 acceptance can be gated open.

## 2. Scope and conventions

### 2.1 Frozen instance

| Dimension | Value |
|---|---|
| Servicer | `MRC` |
| `remit_date` | `2026-04-30` |
| Upstream table snapshot | `snapshots/2026-04-30/raw/mrc/*.parquet` (5 × `mrc.*` tables + 4 × `port.*` tables) |
| Physical baseline file | `baselines/mrc/2026-04-30/validation_report.xlsx` (to be produced by `tools/freeze_baseline.py` at Stage 1.6 wrap-up) |
| Companion metadata | `baselines/mrc/2026-04-30/manifest.json` (writer version, openpyxl version, SHA-256, generation time) |

### 2.2 Two confidence tiers / 两级置信度

Each contract entry below carries either `[FROM-CODE]` or `[VERIFY]`:

- `[FROM-CODE]`: **fully determined by source code**, reverse-engineered from `gen_remit_validation_report.py` (see 1.3 Sheet Rendering Layer (sheets.en.md) § 4). Stage 2 implementers may treat this chapter's description as the contract directly.
- `[VERIFY]`: **requires a measured physical XLSX to settle** (openpyxl default behaviour, `inf` / `NaN` expression, actual auto-fit column widths, presence of freeze panes, ...). This chapter gives the **most-likely** expected value plus how to verify it; once the physical baseline lands the value must be back-filled and the tag upgraded to `[FROM-CODE+VERIFY]`.

### 2.3 Out of scope

- Business numbers themselves (what is `begbal` for some specific loan) — that is a data question, not a render contract.
- Upstream Parquet snapshot schema — see 1.1 Raw Data Layer (rawdata.en.md).
- Stage 2 implementation choices (which writer, which language) — this chapter only defines "must look like this".

## 3. Workbook-level baseline

### 3.1 Sheet inventory and tab order `[FROM-CODE]`

`gen_remit_validation_report.py:1327-1356` registers 5 MRC sheets; the renderer writes them in registration order, so the **final XLSX tab order is fixed**:

| Tab # | Sheet name | Rows | Cols | Highlight cols | Helper |
|---|---|---|---|---|---|
| 1 | `MRC_Summary_check` | 2 (1 header + 1 data) | 14 | 0 | `_summary_columns()` |
| 2 | `MRC_General_Check` | N+1 | 35 | 7 | `_general_columns("mrc_ln")` |
| 3 | `MRC_Advance_Check` | N+1 | 27 | 4 | `_advance_columns("mrc_ln")` |
| 4 | `MRC_ServiceFee_Check` | N+1 | 8 | 1 | `_service_fee_columns("mrc_ln")` |
| 5 | `MRC_Adv_Info` | M+1 | 7 | 0 | `_adv_info_columns()` |

N = number of loans with data for the period (each validator computes its own), M = number of rows after aggregating by `(bucket, description, transaction_code)`. Concrete values of N, M are `[VERIFY]`.

Source: `gen_remit_validation_report.py:1327-1356`; see 1.3 Sheet Rendering Layer (sheets.en.md) § 4.4.

### 3.2 Workbook-level attributes `[VERIFY]`

| Attribute | Expected | Notes |
|---|---|---|
| Workbook default font | ARIAL 12 black non-bold | listed in 1.3 § 4.2; how it overrides openpyxl default needs measurement |
| Active tab | tab 1 `MRC_Summary_check` | openpyxl default = first written; verify |
| Workbook properties (creator / title / lastModifiedBy) | openpyxl default (unset or writer-version string) | Stage 2 should reproduce "unset" to preserve cell-identity |
| Calculation properties | unset | XLSX evaluated on demand when Excel opens; writer does not pre-compute |
| Defined names | none | renderer never creates named ranges |
| Shared-strings table entries | dedupe-union of str columns | verify; useful as sanity check only |

### 3.3 Per-sheet workbook view attributes `[VERIFY]`

| Attribute | Expected |
|---|---|
| Freeze panes (`view.freezePanes`) | **unset** (source never calls `freeze_panes`; verify) |
| Show gridlines | True (openpyxl default) |
| Show row & column headers | True (openpyxl default) |
| Zoom scale | 100 (openpyxl default) |
| Tab color | unset |
| Sheet visibility | visible |

> ⚠️ If `[VERIFY]` confirms the source does not freeze the header but UX-wise "row 1 scrolls away" is annoying — that becomes a Stage 2 improvement proposal (logged in `decisions.md`, not silently changing baseline).

## 4. Header baseline

### 4.1 Common header attributes `[FROM-CODE]`

`gen_remit_validation_report.py:1742-1761` (`header_format`) runs once per sheet. **All** header cells (regardless of highlight status):

| Attribute | Value | Source |
|---|---|---|
| Font name | `ARIAL` | style block at `:19-86` |
| Font size | `12` | same |
| Font bold | `True` | same |
| Font colour (non-highlight) | black `#000000` | same |
| Alignment horizontal | `center` | same |
| Alignment vertical | `center` | same |
| Border | thin black on all four sides (`Side(style='thin', color='000000')`) | same |

### 4.2 Header fill RGB `[FROM-CODE]`

| Type | Fill RGB | Font colour | Applies to |
|---|---|---|---|
| **Normal header** (`header_style`) | `bccde9` (light blue) | black | every non-highlight column's header |
| **Highlight header** (`diff_column_header_style`) | `ffc7ce` (pink) | `df5006` (orange) | the 12 highlight headers (`MRC_General_Check` × 7 + `MRC_Advance_Check` × 4 + `MRC_ServiceFee_Check` × 1) |

Source: `gen_remit_validation_report.py:19-86` (style definition) + `:1742-1761` (application logic).

### 4.3 Per-sheet header layout `[FROM-CODE]`

| Sheet | Header row | Normal-header cols | Highlight-header cols |
|---|---|---|---|
| `MRC_Summary_check` | 1 | 1–14 (all) | 0 |
| `MRC_General_Check` | 1 | 1–5, 7–8, 10–11, 13–14, 16–20, 22–23, 25–26, 28–35 (28 cols) | 6, 9, 12, 15, 21, 24, 27 (7 cols) |
| `MRC_Advance_Check` | 1 | 1–8, 10–13, 15–18, 20–23, 25–27 (23 cols) | 9, 14, 19, 24 (4 cols) |
| `MRC_ServiceFee_Check` | 1 | 1–6, 8 (7 cols) | 7 (1 col: `servicefee_diff`) |
| `MRC_Adv_Info` | 1 | 1–7 (all) | 0 |

Exact highlight positions: 1.3 Sheet Rendering Layer (sheets.en.md) §§ 5–9 column catalogs.

### 4.4 Header row height `[VERIFY]`

Source does not set row height explicitly; expected openpyxl default (≈ 15 pt). Back-fill the exact value once the physical baseline lands.

## 5. Body cell baseline per data_type

### 5.1 `data_type == "money"` `[FROM-CODE]`

Logic (`gen_remit_validation_report.py:1721-1739`):

| Value case | Written value | `number_format` | Notes |
|---|---|---|---|
| empty / `None` / `NaN` | `0` (coerced) | `$#,##0` (`money_int_format`) | empty and 0 become indistinguishable in XLSX |
| integer-valued (`value == int(float(value))`) | original | `$#,##0` | e.g. `1500.0` → `$1,500` |
| non-integer | rounded original | `$#,##0.00` (`money_format`) | rounding already done in `sheet_df_round` (2dp) |

Negative-value rendering is decided by `number_format` itself: `$#,##0.00` renders negatives as `-$1,234.56` (leading minus, no parentheses) in Excel. `[VERIFY]` once measured.

Applies to: every column with `data_type == money` (see 1.3 §§ 5–9 / 1.4 Field Definitions (fields.en.md) data_type column).

### 5.2 `data_type == "float"` `[FROM-CODE]`

Logic: **no** `number_format` is set. The value is written as a plain rounded number (`sheet_df_round` rounds to 2dp before write).

| Value case | Written | `number_format` | Excel rendering |
|---|---|---|---|
| finite number | round(value, 2) | `General` (openpyxl default) | `1.23` / `-0.05` |
| `NaN` | NaN | `General` | `[VERIFY]` — openpyxl default likely writes an empty cell (NaN cannot serialise as OOXML number); confirm |
| `+inf` / `-inf` | inf | `General` | `[VERIFY]` — openpyxl writes OOXML `<v>` element value; Excel may show `1.7976931348623157E+308` or an inline error; see § 8 |

Applies to: every `_diff_remitvsdaily` numeric-diff column in `MRC_General_Check`, every `intrate_*`, and `amt_MoM` in `MRC_Adv_Info`.

### 5.3 `data_type == "date"` `[FROM-CODE+VERIFY]`

Logic: renderer does not set `number_format`; values are serialised by pandas' default Excel serialiser (Python `date` / `datetime` → Excel serial number).

| Attribute | Expected |
|---|---|
| Cell `value` type | Excel serial number (float) |
| `number_format` | `[VERIFY]` — likely openpyxl auto-assigns `yyyy-mm-dd h:mm:ss` for datetimes; concrete format must be measured |
| Time zone | none (pandas serialises as naive) |

Applies to: `asofdate` (all 5 sheets), `nextduedate_remit` / `nextduedate_daily` (General), `fctrdt` (ServiceFee).

### 5.4 `data_type == "str"` `[FROM-CODE]`

Logic: renderer does not set `number_format`. Value is written into the XLSX shared-strings table.

| Attribute | Value |
|---|---|
| Cell value | original string |
| `number_format` | `General` |
| Empty string | written as empty string (not coerced to 0) |

Applies to: `loanid`, `dealid`, `mrc_ln`, `delq_status`, `delinquency_status_mba`, `bucket`, `description`, `transaction_code`.

### 5.5 `data_type == "percentage"` `[N/A FOR MRC]`

No MRC column uses this type; listed here for completeness only. If mis-used it would apply `0.00%` (`percent_format`). `intrate_*` columns are **deliberately** declared `float` rather than `percentage` — see 1.3 § 4.2 + 1.4 Field Definitions (fields.en.md) § 5 gap 1.

### 5.6 Default body cell attributes `[FROM-CODE]`

Base style applied regardless of data type (from the style block at `gen_remit_validation_report.py:19-86`):

| Attribute | Value |
|---|---|
| Font name | `ARIAL` |
| Font size | `12` |
| Font colour | black `#000000` (diff-highlight cells excluded — see § 6) |
| Font bold | `False` (diff-highlight cells excluded) |
| Alignment horizontal | default (openpyxl unset — number / string each follow their own default) |
| Alignment vertical | `[VERIFY]` |
| Border | thin black on all four sides (`Side(style='thin', color='000000')`) |

## 6. Diff highlight cell baseline

### 6.1 Trigger condition `[FROM-CODE]`

`diff_cell_format` (`gen_remit_validation_report.py:1764-1798`): for each highlight column `c` of each sheet:

```text
mask = pd.to_numeric(df[c], errors='coerce').abs() > 0
```

Rows where `mask == True` get the diff style applied. Detailed rules: 1.5 Validation Rules (rules.en.md) § 3.1 and § 3.2.

| Value case | Highlighted? | Notes |
|---|---|---|
| number > 0 or < 0 | ✅ yes | strict `> 0`, exactly 0 does not highlight |
| `0` | ❌ no | business-wise "exactly aligned" |
| `NaN` / `None` | ❌ no | `pd.to_numeric(errors='coerce')` → `NaN`, `NaN.abs() > 0` is `False` |
| non-numeric string | ❌ no | coerces to `NaN` |

### 6.2 Diff cell style `[FROM-CODE]`

| Attribute | Value | Source |
|---|---|---|
| Fill RGB | `ffc7ce` (pink) | `:19-86` `diff_column_style` |
| Font colour | `df5006` (orange) | same |
| Font bold | inherits body default (False) | `[VERIFY]` |
| Font name / size | `ARIAL` / `12` (same as body) | same |
| Border | same as body (thin black on all four sides) | same |
| `number_format` | inherits the column's `data_type`-derived format | diff does not reset number_format |

### 6.3 Distribution of the 12 highlighted columns `[FROM-CODE]`

| Sheet | Highlighted columns | Count |
|---|---|---|
| `MRC_General_Check` | `intrate_diff_remitvsdaily`, `nextduedate_diff_remitvsdaily`, `begbal_diff_remitvsdaily`, `endbal_diff_remitvsdaily`, `deferredprincipal_diff_remitvsdaily`, `deferredint_diff_remitvsdaily`, `pandi_schedule_diff_remitvsdaily` | 7 |
| `MRC_Advance_Check` | `escadv_diff_remitvsdaily`, `recovcorpadv_diff_remitvsdaily`, `nonrecovcorpadv_diff_remitvsdaily`, `totalcorpadv_diff_remitvsdaily` | 4 |
| `MRC_ServiceFee_Check` | `servicefee_diff` | 1 |
| **Total** | | **12** |

Source: `gen_remit_validation_report.py:1331-1339, 1345-1348, 1354`.

### 6.4 "Should-have-been-highlighted but isn't" — known design exemption `[FROM-CODE]`

- `pandi_diff_remitvsdaily` (column 31 of `MRC_General_Check`) — actual-P&I delta, **deliberately** excluded from the highlight list (noise floor too high); see 1.3 § 6.1 gap 1 and 1.5 Validation Rules (rules.en.md).

## 7. Column widths and miscellaneous body attributes

### 7.1 Column width `[FROM-CODE+VERIFY]`

`automatic_column_width: True` (see 1.3 § 4.2) lets the renderer auto-fit by content, falling back to `default_column_width = 20`. **Actual widths** depend on data and must be measured:

| Sheet | Column | Expected width (units ≈ char width) |
|---|---|---|
| all | `asofdate` | `[VERIFY]` — likely `10` (e.g. `2026-04-30`) |
| `MRC_Adv_Info` | `description` | `[VERIFY]` — depends on longest string |
| `MRC_General_Check` | `delinquency_status_mba` | `[VERIFY]` |
| others | numeric / short-string columns | `[VERIFY]` — most expected `20` |

Once the physical baseline lands, back-fill the exact value table into this section.

### 7.2 Empty sheet / empty DataFrame fallback `[FROM-CODE]`

If a validator returns `None` due to an exception (see 1.5 § 9.1), its entry in `VALIDATION_TABLE_MAP` is `None` and the renderer silently skips → **that sheet tab does not appear in the XLSX**. The cell-identity harness must therefore:

- if baseline has all 5 sheets, Stage 2 must too;
- if baseline is missing some sheet (a known validator-failure silent-skip), Stage 2 must omit the same one.

## 8. Edge cases requiring physical verification

### 8.1 `±inf` rendering `[VERIFY]`

`MRC_Adv_Info.amt_MoM = amt / amt_1m - 1` produces `+inf` or `-inf` when `amt_1m == 0` (sign depending on `amt`). `data_type_format` does **not** set a `number_format` for float columns; the most likely openpyxl default behaviour is:

- written as the OOXML `<v>` element with textual content `inf` / `1.7976931348623157E+308` (Python `repr(float('inf'))` = `'inf'`, but openpyxl's `_write_cell` does `str(value)` at write time);
- Excel renders as `#NUM!` or as the literal string `inf`, depending on Excel version.

**Stage 2 must first measure the baseline's actual expression and then decide how to reproduce it.** If the baseline contains the string `inf`, Stage 2 writes the same; if `#NUM!`, Stage 2 emits an Excel error object.

### 8.2 `NaN` rendering `[VERIFY]`

Can arise in:

- `MRC_General_Check` reindex padding a missing column with `np.nan` (only when SQL projection is missing — currently verified to be non-missing, so this branch is dead code today, but Stage 2 must preserve the behaviour);
- `MRC_ServiceFee_Check.servicefee_diff` becomes `NaN` when `port.portmonth` outer-join misses the loan (gap 4 silent-miss).

Expected openpyxl default: write as empty cell (NaN cannot serialise as OOXML number). `[VERIFY]`.

### 8.3 Empty money cells `[FROM-CODE]`

`data_type_format` coerces empty money cells to `0` (applies `$#,##0`). Therefore **no empty money cell ever appears in baseline** — every money cell is either a number or `$0`.

### 8.4 Date cells with `None` `[VERIFY]`

If a date column carries `None` (e.g. `nextduedate_daily` missing), pandas writes an empty cell by default. `[VERIFY]`.

## 9. Verification checklist (gating Stage 2 acceptance)

Once the physical baseline `baselines/mrc/2026-04-30/validation_report.xlsx` lands, **each row below must be upgraded from `[VERIFY]` to `[CONFIRMED]`** before Stage 2 acceptance can be gated open.

| # | Item | Section | Current | Target |
|---|---|---|---|---|
| V1 | Workbook default font actually written | § 3.2 | `[VERIFY]` | `[CONFIRMED]` |
| V2 | Whether any sheet sets freeze_panes | § 3.3 | `[VERIFY]` | `[CONFIRMED]` |
| V3 | Data row counts N (general/advance/service_fee) and M (adv_info) | § 3.1 | `[VERIFY]` | `[CONFIRMED]` |
| V4 | Header row height | § 4.4 | `[VERIFY]` | `[CONFIRMED]` |
| V5 | Money negative-value `number_format` actual rendering | § 5.1 | `[VERIFY]` | `[CONFIRMED]` |
| V6 | float `NaN` actual written form | § 5.2 / § 8.2 | `[VERIFY]` | `[CONFIRMED]` |
| V7 | float `±inf` actual written form | § 5.2 / § 8.1 | `[VERIFY]` | `[CONFIRMED]` |
| V8 | date column `number_format` actual value | § 5.3 | `[VERIFY]` | `[CONFIRMED]` |
| V9 | Body cell vertical alignment | § 5.6 | `[VERIFY]` | `[CONFIRMED]` |
| V10 | Diff cell font bold inheritance | § 6.2 | `[VERIFY]` | `[CONFIRMED]` |
| V11 | Per-column auto-fit width table | § 7.1 | `[VERIFY]` | `[CONFIRMED]` |
| V12 | Date `None` cell expression | § 8.4 | `[VERIFY]` | `[CONFIRMED]` |

## 10. How to produce the physical baseline

### 10.1 Tooling contract

```text
tools/freeze_baseline.py mrc 2026-04-30
  ⟶ baselines/mrc/2026-04-30/validation_report.xlsx
  ⟶ baselines/mrc/2026-04-30/manifest.json
     {
       "servicer": "MRC",
       "remit_date": "2026-04-30",
       "generated_at_utc": "...",
       "writer": "openpyxl",
       "writer_version": "...",
       "python_version": "...",
       "sha256": "...",
       "snapshot_source": "snapshots/2026-04-30/raw/mrc/"
     }
```

`tools/freeze_baseline.py` is yet to be implemented (belongs to the `mrc-source-baseline` todo); its responsibilities are:

1. load the frozen Parquet snapshot;
2. invoke the legacy PrefectFlow entry point `util/gen_remit_validation_report.py` (via a thin Redshift-adapter-reads-Parquet shim — see `mrc-source-baseline` todo);
3. write `baselines/mrc/2026-04-30/validation_report.xlsx`;
4. compute SHA-256 and persist the manifest.

### 10.2 Verification workflow

1. Run `tools/freeze_baseline.py mrc 2026-04-30` to generate the physical file;
2. Run `tools/inspect_baseline.py mrc 2026-04-30` (to be implemented) against the 12 V-checks in § 9 and back-fill the results into this chapter;
3. Upgrade the § 9 table to `[CONFIRMED]`, bump `Revision history` to v2, and add a record to `decisions.md`;
4. `git add` the baseline file and the manifest; depending on size, decide whether to use git-lfs (baselines are not in the default `.gitignore` exclusion set and may be tracked).

## 11. Source citation index

| Subsystem | File + lines | Purpose |
|---|---|---|
| Style block | `util/gen_remit_validation_report.py:19-86` | every `*_format` / `*_style` / font / colour / border definition |
| Helper functions | `util/gen_remit_validation_report.py:1157-1177` | `_validation_report_col`, `_validation_report_sheet` |
| 5 MRC sheet registry entries | `util/gen_remit_validation_report.py:1327-1356` | sheet name → helper + highlight |
| `data_type_format` rendering | `util/gen_remit_validation_report.py:1721-1739` | money / percentage / other `number_format` decisions |
| `header_format` | `util/gen_remit_validation_report.py:1742-1761` | normal / highlight header style application |
| `diff_cell_format` | `util/gen_remit_validation_report.py:1764-1798` | highlight-column mask + diff style brushing |
| `MRC_Summary_check` column helper | `util/gen_remit_validation_report.py:1180-1196` | 14-column definition |
| `MRC_General_Check` column helper | `util/gen_remit_validation_report.py:1199-1236` | 35-column definition |
| `MRC_Advance_Check` column helper | `util/gen_remit_validation_report.py:1239-1268` | 27-column definition |
| `MRC_ServiceFee_Check` column helper | `util/gen_remit_validation_report.py:1271-1281` | 8-column definition |
| `MRC_Adv_Info` column helper | `util/gen_remit_validation_report.py:1284-1293` | 7-column definition |

Further rendering cross-references: 1.3 Sheet Rendering Layer (sheets.en.md) § 4; rule cross-references: 1.5 Validation Rules (rules.en.md) § 3.
