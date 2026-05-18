"""Builder for ``MRC_Adv_Info`` (7 cols, 0 highlight).

Chapter reference: ``docs/mrc/1.3-sheets.en.md`` § 9. Producing
validator: ``mrc_other_check`` (``mrc_validation.py:105-158``).
"""

from __future__ import annotations

from whitebox.sheets.base import ColumnSpec, SheetModel, ValidatorOutput
from whitebox.sheets.mrc._helpers import asofdate_metadata, build_data_rows

# 1.3 § 9.1 — 7 columns; informational sheet, no highlight columns.
# Gap 5 (1.3 § 9 / § 10 #5): ``amt_MoM`` is ``float`` (no
# number_format), so validator-produced ``±inf`` / ``NaN`` flow through
# verbatim — the renderer / Excel does the rest.
COLUMNS: tuple[ColumnSpec, ...] = (
    ColumnSpec("bucket", "str"),
    ColumnSpec("description", "str"),
    ColumnSpec("transaction_code", "str"),
    ColumnSpec("amt", "money", round_to=2),
    ColumnSpec("amt_1m", "money", round_to=2),
    ColumnSpec("amt_MoM", "float", round_to=2),
    ColumnSpec("asofdate", "date"),
)

SHEET_NAME = "MRC_Adv_Info"
SHEET_ID = SHEET_NAME
SERVICER = "MRC"
TAB_ORDER = 5


def build(inputs: ValidatorOutput) -> SheetModel:
    return SheetModel(
        sheet_name=SHEET_NAME,
        columns=COLUMNS,
        rows=build_data_rows(inputs.df, COLUMNS),
        # Freeze header + the three string discriminators so ``amt`` /
        # ``amt_1m`` / ``amt_MoM`` stay aligned during horizontal scroll.
        freeze_panes="D2",
        metadata=asofdate_metadata(inputs),
    )
