"""Builder for ``MRC_Summary_check`` (14 cols, 0 highlight).

Chapter reference: ``docs/mrc/1.3-sheets.en.md`` § 5 (column catalog +
rendering specifics). Producing validator: ``mrc_summary_check``
(``mrc_validation.py:8-36``).
"""

from __future__ import annotations

from whitebox.sheets.base import ColumnSpec, SheetModel, ValidatorOutput
from whitebox.sheets.mrc._helpers import asofdate_metadata, build_data_rows

# 1.3 § 5.1 — 14 columns, all money + asofdate, no highlights.
COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("principalreceived", "money", round_to=2),
    ColumnSpec("interestreceived", "money", round_to=2),
    ColumnSpec("escrowadv_chg", "money", round_to=2),
    ColumnSpec("corpadvrec_chg", "money", round_to=2),
    ColumnSpec("corpadvnonrec_chg", "money", round_to=2),
    ColumnSpec("corpadvtotal_chg", "money", round_to=2),
    ColumnSpec("servicefee", "money", round_to=2),
    ColumnSpec("otherfees", "money", round_to=2),
    ColumnSpec("totalservicefee", "money", round_to=2),
    ColumnSpec("subremit", "money", round_to=2),
    ColumnSpec("totremit", "money", round_to=2),
    ColumnSpec("beginningbalance", "money", round_to=2),
    ColumnSpec("endingbalance", "money", round_to=2),
    ColumnSpec("asofdate", "date"),
)

SHEET_NAME = "MRC_Summary_check"
SHEET_ID = SHEET_NAME
SERVICER = "MRC"
TAB_ORDER = 1


def build(inputs: ValidatorOutput) -> SheetModel:
    """Construct the ``MRC_Summary_check`` sheet model.

    Per 1.3 § 5.2: 1 portfolio-level data row, every helper-declared
    column either present or coerced to ``np.nan`` (here: ``None``).
    """
    return SheetModel(
        sheet_name=SHEET_NAME,
        columns=COLUMNS,
        rows=build_data_rows(inputs.df, COLUMNS),
        # Freeze just below the header so the single data row stays in
        # view alongside the headers as users scroll horizontally.
        freeze_panes="A2",
        metadata=asofdate_metadata(inputs),
    )
