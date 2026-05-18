"""Builder for ``MRC_General_Check`` (35 cols, 7 highlight).

Chapter reference: ``docs/mrc/1.3-sheets.en.md`` § 6. Producing
validator: ``mrc_check_general_info`` (``mrc_validation.py:57-72``).
"""

from __future__ import annotations

from whitebox.sheets.base import ColumnSpec, SheetModel, ValidatorOutput
from whitebox.sheets.mrc._helpers import asofdate_metadata, build_data_rows

# 1.3 § 6.1 — 35 columns; 7 highlight columns marked ``highlight=True``.
# Column order is the helper order from ``_general_columns("mrc_ln")``;
# every column either projects from the SQL or is coerced to ``None`` per
# the legacy reindex behavior (1.3 § 3).
COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("loanid", "str"),
    ColumnSpec("mrc_ln", "str"),                     # from loan_column="mrc_ln"
    ColumnSpec("dealid", "str"),
    ColumnSpec("intrate_remit", "float", round_to=2),
    ColumnSpec("intrate_daily", "float", round_to=2),
    ColumnSpec("intrate_diff_remitvsdaily", "float", round_to=2, highlight=True),
    ColumnSpec("nextduedate_remit", "date"),
    ColumnSpec("nextduedate_daily", "date"),
    # 1.3 § 10 gap 2: typed float w/ round_to=2 even though it is a
    # day-count diff — preserved verbatim for cell-identity.
    ColumnSpec("nextduedate_diff_remitvsdaily", "float", round_to=2, highlight=True),
    ColumnSpec("begbal_remit", "money", round_to=2),
    ColumnSpec("begbal_daily", "money", round_to=2),
    ColumnSpec("begbal_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("endbal_remit", "money", round_to=2),
    ColumnSpec("endbal_daily", "money", round_to=2),
    ColumnSpec("endbal_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("principal_remit", "money", round_to=2),
    ColumnSpec("interest_remit", "money", round_to=2),
    ColumnSpec("prin_bal_diff_remit", "money", round_to=2),
    ColumnSpec("deferredprincipal_remit", "money", round_to=2),
    ColumnSpec("deferredprincipal_daily", "money", round_to=2),
    ColumnSpec("deferredprincipal_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("deferredint_remit", "money", round_to=2),
    ColumnSpec("deferredint_daily", "money", round_to=2),
    ColumnSpec("deferredint_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("pandi_remit", "money", round_to=2),
    ColumnSpec("pandiexpected_daily", "money", round_to=2),
    ColumnSpec("pandi_schedule_diff_remitvsdaily", "money", round_to=2, highlight=True),
    ColumnSpec("principalreceived_daily", "money", round_to=2),
    ColumnSpec("interestreceived_daily", "money", round_to=2),
    ColumnSpec("pandireceived_daily", "money", round_to=2),
    # 1.3 § 10 gap 1: pandi_diff_remitvsdaily is intentionally NOT
    # highlighted; pandi_schedule_diff_remitvsdaily is.
    ColumnSpec("pandi_diff_remitvsdaily", "money", round_to=2),
    ColumnSpec("pandi_paid_times_remit", "float", round_to=2),
    ColumnSpec("pandi_paid_times_daily", "float", round_to=2),
    ColumnSpec("delinquency_status_mba", "str"),
    ColumnSpec("asofdate", "date"),
)

SHEET_NAME = "MRC_General_Check"
SHEET_ID = SHEET_NAME
SERVICER = "MRC"
TAB_ORDER = 2


def build(inputs: ValidatorOutput) -> SheetModel:
    return SheetModel(
        sheet_name=SHEET_NAME,
        columns=COLUMNS,
        rows=build_data_rows(inputs.df, COLUMNS),
        # Freeze header + first three identifier columns so analysts can
        # scroll through the 7 diff blocks without losing loan context.
        freeze_panes="D2",
        metadata=asofdate_metadata(inputs),
    )
