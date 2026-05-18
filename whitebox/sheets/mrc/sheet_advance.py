"""Builder for ``MRC_Advance_Check`` (27 cols, 4 highlight).

Chapter reference: ``docs/mrc/1.3-sheets.en.md`` § 7. Producing
validator: ``mrc_check_adv_balance`` (``mrc_validation.py:39-54``).
"""

from __future__ import annotations

from whitebox.sheets.base import ColumnSpec, SheetModel, ValidatorOutput
from whitebox.sheets.mrc._helpers import asofdate_metadata, build_data_rows

# 1.3 § 7.1 — 27 columns; 4 highlight columns (4 advance-bucket diffs).
# Naming asymmetry (1.3 § 7 gap 3 / § 10 #3): the diff column uses the
# ``recov`` prefix while the per-period source columns use ``rec`` —
# preserved verbatim for cell-identity.
COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("loanid", "str"),
    ColumnSpec("mrc_ln", "str"),                     # from loan_column="mrc_ln"
    ColumnSpec("dealid", "str"),
    ColumnSpec("delq_status", "str"),
    ColumnSpec("escrowadv_prev_daily", "money", round_to=2),
    ColumnSpec("escrowadv_curr_daily", "money", round_to=2),
    ColumnSpec("escrowadv_chg_daily", "money", round_to=2),
    ColumnSpec("escadv_remit", "money", round_to=2),
    ColumnSpec("escadv_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("reccorpadvance_prev_daily", "money", round_to=2),
    ColumnSpec("reccorpadvance_curr_daily", "money", round_to=2),
    ColumnSpec("reccorpadvance_chg_daily", "money", round_to=2),
    ColumnSpec("reccorpadvance_remit", "money", round_to=2),
    ColumnSpec("recovcorpadv_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("nonrecovcorpadv_prev_daily", "money", round_to=2),
    ColumnSpec("nonrecovcorpadv_curr_daily", "money", round_to=2),
    ColumnSpec("nonrecovcorpadv_chg_daily", "money", round_to=2),
    ColumnSpec("nonrecovadvance_remit", "money", round_to=2),
    ColumnSpec("nonrecovcorpadv_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("totalcorpadv_prev_daily", "money", round_to=2),
    ColumnSpec("totalcorpadv_curr_daily", "money", round_to=2),
    ColumnSpec("totalcorpadv_chg_daily", "money", round_to=2),
    ColumnSpec("totalcorpadvance_remit", "money", round_to=2),
    ColumnSpec("totalcorpadv_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("escrow_balance_prev", "money", round_to=2),
    ColumnSpec("escrow_balance_curr", "money", round_to=2),
    ColumnSpec("asofdate", "date"),
)

SHEET_NAME = "MRC_Advance_Check"
SHEET_ID = SHEET_NAME
SERVICER = "MRC"
TAB_ORDER = 3


def build(inputs: ValidatorOutput) -> SheetModel:
    return SheetModel(
        sheet_name=SHEET_NAME,
        columns=COLUMNS,
        rows=build_data_rows(inputs.df, COLUMNS),
        # Same identifier-column freeze pattern as General_Check
        # (loanid, mrc_ln, dealid, delq_status all stay visible).
        freeze_panes="E2",
        metadata=asofdate_metadata(inputs),
    )
