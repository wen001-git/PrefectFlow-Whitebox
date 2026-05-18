"""Tests for ``whitebox.sheets.mrc.sheet_service_fee``.

Chapter ref: ``docs/mrc/1.3-sheets.en.md`` § 8 (MRC_ServiceFee_Check).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from whitebox.sheets.base import ValidatorOutput
from whitebox.sheets.mrc import sheet_service_fee

# § 8.1 — 8 columns; ``servicefee_diff`` is the only highlight.
EXPECTED_COLUMNS = (
    "fctrdt",
    "loanid",
    "mrc_ln",
    "dealid",
    "servicefee_remit_raw",
    "servicefee_portmonth",
    "servicefee_diff",
    "asofdate",
)


def _inputs(df: pd.DataFrame) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id="mrc_service_fee_check",
        servicer="MRC",
        df=df,
        asofdate=date(2026, 4, 30),
    )


def test_empty_input() -> None:
    model = sheet_service_fee.build(_inputs(pd.DataFrame()))
    assert model.sheet_name == "MRC_ServiceFee_Check"
    assert model.rows == ()
    assert model.column_keys() == EXPECTED_COLUMNS
    assert model.highlight_keys() == ("servicefee_diff",)


def test_happy_path_two_rows() -> None:
    df = pd.DataFrame(
        [
            {
                "fctrdt": date(2026, 5, 1),
                "loanid": "L1", "mrc_ln": "MRC1", "dealid": "D1",
                "servicefee_remit_raw": 100.0,
                "servicefee_portmonth": 100.0,
                "servicefee_diff": 0.0,
            },
            {
                "fctrdt": date(2026, 5, 1),
                "loanid": "L2", "mrc_ln": "MRC2", "dealid": "D2",
                "servicefee_remit_raw": 120.0,
                "servicefee_portmonth": 100.0,
                "servicefee_diff": 20.0,  # → highlight
            },
        ]
    )
    model = sheet_service_fee.build(_inputs(df))
    assert len(model.rows) == 2

    diff_idx = list(model.column_keys()).index("servicefee_diff")
    assert "diff" not in model.rows[0].cells[diff_idx].style.classes
    assert "diff" in model.rows[1].cells[diff_idx].style.classes
    # fctrdt cell flows as a date.
    assert model.rows[0].cells[0].value == date(2026, 5, 1)
    assert "date" in model.rows[0].cells[0].style.classes


def test_edge_case_null_diff_does_not_highlight() -> None:
    # § 8 gap 4: outer-join miss → servicefee_diff is NULL; must NOT
    # highlight (silent miss is documented and preserved).
    df = pd.DataFrame(
        [
            {
                "fctrdt": date(2026, 5, 1),
                "loanid": "L_orphan",
                "mrc_ln": "MRC_O",
                "dealid": "D",
                "servicefee_remit_raw": 50.0,
                "servicefee_portmonth": None,
                "servicefee_diff": None,
            }
        ]
    )
    model = sheet_service_fee.build(_inputs(df))
    diff_idx = list(model.column_keys()).index("servicefee_diff")
    cell = model.rows[0].cells[diff_idx]
    # None money → coerced to 0 per § 4.2; no highlight (0 is not > 0).
    assert cell.value == 0
    assert "diff" not in cell.style.classes


def test_column_presence_matches_chapter_spec() -> None:
    model = sheet_service_fee.build(_inputs(pd.DataFrame()))
    assert model.column_keys() == EXPECTED_COLUMNS
    money_cols = {c.key for c in model.columns if c.data_type == "money"}
    assert money_cols == {
        "servicefee_remit_raw",
        "servicefee_portmonth",
        "servicefee_diff",
    }
