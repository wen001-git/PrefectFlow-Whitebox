"""Builder for ``MRC_ServiceFee_Check`` (8 cols, 1 highlight).

Chapter reference: ``docs/mrc/1.3-sheets.en.md`` § 8. Producing
validator: ``mrc_service_fee_check`` (``mrc_validation.py:75-102``).
"""

from __future__ import annotations

from whitebox.sheets.base import ColumnSpec, SheetModel, ValidatorOutput
from whitebox.sheets.mrc._helpers import asofdate_metadata, build_data_rows

# 1.3 § 8.1 — 8 columns; ``servicefee_diff`` is the lone highlight.
# Gap 4 (1.3 § 10 #4): ``fctrdt`` and ``asofdate`` are intentionally
# both present (different semantics) — preserved for cell-identity.
COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("fctrdt", "date"),
    ColumnSpec("loanid", "str"),
    ColumnSpec("mrc_ln", "str"),                     # from loan_column="mrc_ln"
    ColumnSpec("dealid", "str"),
    ColumnSpec("servicefee_remit_raw", "money", round_to=2),
    ColumnSpec("servicefee_portmonth", "money", round_to=2),
    ColumnSpec("servicefee_diff", "money", round_to=2, highlight=True),
    ColumnSpec("asofdate", "date"),
)

SHEET_NAME = "MRC_ServiceFee_Check"
SHEET_ID = SHEET_NAME
SERVICER = "MRC"
TAB_ORDER = 4


def build(inputs: ValidatorOutput) -> SheetModel:
    return SheetModel(
        sheet_name=SHEET_NAME,
        columns=COLUMNS,
        rows=build_data_rows(inputs.df, COLUMNS),
        # Freeze header + the four identifier columns (fctrdt, loanid,
        # mrc_ln, dealid) so the two amounts + diff stay legible.
        freeze_panes="E2",
        metadata=asofdate_metadata(inputs),
    )
