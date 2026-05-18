"""Tests for ``whitebox.sheets.mrc.sheet_summary``.

Chapter ref: ``docs/mrc/1.3-sheets.en.md`` § 5 (MRC_Summary_check).
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from whitebox.sheets.base import ValidatorOutput
from whitebox.sheets.mrc import sheet_summary

# Per 1.3 § 5.1 — 14 columns, ending with asofdate, no highlights.
EXPECTED_COLUMNS = (
    "principalreceived",
    "interestreceived",
    "escrowadv_chg",
    "corpadvrec_chg",
    "corpadvnonrec_chg",
    "corpadvtotal_chg",
    "servicefee",
    "otherfees",
    "totalservicefee",
    "subremit",
    "totremit",
    "beginningbalance",
    "endingbalance",
    "asofdate",
)


def _inputs(df: pd.DataFrame) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id="mrc_summary_check",
        servicer="MRC",
        df=df,
        asofdate=date(2026, 4, 30),
    )


def test_empty_input_produces_header_only_model() -> None:
    model = sheet_summary.build(_inputs(pd.DataFrame()))
    assert model.sheet_name == "MRC_Summary_check"
    assert model.rows == ()
    assert model.column_keys() == EXPECTED_COLUMNS
    assert model.highlight_keys() == ()  # § 5 — no highlight columns


def test_happy_path_single_row() -> None:
    df = pd.DataFrame(
        [
            {
                "principalreceived": 1500.55,
                "interestreceived": 200.25,
                "escrowadv_chg": 10,
                "corpadvrec_chg": 0,
                "corpadvnonrec_chg": 5.5,
                "corpadvtotal_chg": 5.5,
                "servicefee": 100,
                "otherfees": 0,
                "totalservicefee": 100,
                "subremit": 50,
                "totremit": 1850.30,
                "beginningbalance": 9_000_000.00,
                "endingbalance": 8_998_300.00,
                "asofdate": date(2026, 4, 30),
            }
        ]
    )
    model = sheet_summary.build(_inputs(df))
    assert len(model.rows) == 1
    row = model.rows[0]
    assert len(row.cells) == 14
    # principalreceived is non-integer → money style + 2dp
    assert row.cells[0].value == pytest.approx(1500.55)
    assert "money" in row.cells[0].style.classes
    # escrowadv_chg is integer-valued → money-int style
    assert row.cells[2].value == 10
    assert "money-int" in row.cells[2].style.classes
    # asofdate must be a date object
    assert row.cells[13].value == date(2026, 4, 30)
    assert "date" in row.cells[13].style.classes


def test_missing_money_coerced_to_zero_edge_case() -> None:
    # § 4.2 — empty money cell must coerce to 0 and use money-int style.
    df = pd.DataFrame(
        [
            {
                "principalreceived": None,
                "interestreceived": float("nan"),
                "escrowadv_chg": 0,
                "asofdate": date(2026, 4, 30),
            }
        ]
    )
    model = sheet_summary.build(_inputs(df))
    row = model.rows[0]
    # None → 0 (int), money-int style
    assert row.cells[0].value == 0
    assert "money-int" in row.cells[0].style.classes
    # NaN → 0 likewise
    assert row.cells[1].value == 0
    # Missing-from-df columns become None-money → also 0
    assert row.cells[5].value == 0


def test_column_order_matches_chapter_spec() -> None:
    model = sheet_summary.build(_inputs(pd.DataFrame()))
    assert model.column_keys() == EXPECTED_COLUMNS
    # All but the last (asofdate) are declared money with round_to=2.
    for col in model.columns[:-1]:
        assert col.data_type == "money"
        assert col.round_to == 2
    assert model.columns[-1].data_type == "date"
    assert model.metadata["validator_id"] == "mrc_summary_check"
    assert model.metadata["asofdate"] == "2026-04-30"
