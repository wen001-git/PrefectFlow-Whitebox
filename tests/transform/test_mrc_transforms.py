"""Shape tests for the MRC pure transforms.

Every fixture frame mirrors the column projection of the legacy SQL queried
in ``PrefectFlow/flow/remit_validation/mrc_validation.py`` (READ-ONLY sibling
repo). Assertions are about shapes, stamping, immutability, and pandas merge
semantics — never IO.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from pandas import DataFrame

from whitebox.transform import (
    ADVANCE_TABLE_COLUMNS,
    ASOFDATE,
    GENERAL_CHECK_COLUMNS,
    OTHER_CHECK_COLUMNS,
    REMIT_SUMMARY_COLUMNS,
    ServicerId,
    prepare_advance_table,
    prepare_general_check_inputs,
    prepare_other_check,
    prepare_remit_summary,
)

REMIT_DATE = date(2026, 4, 30)


def _row(cols: tuple[str, ...], fill: float = 1.0) -> DataFrame:
    return DataFrame([dict.fromkeys(cols, fill)])


# ---------------------------------------------------------------------------
# Case 1 — RemitSummary happy path
# ---------------------------------------------------------------------------

def test_prepare_remit_summary_stamps_and_keeps_columns() -> None:
    df = _row(REMIT_SUMMARY_COLUMNS, fill=42.0)
    result = prepare_remit_summary(df, REMIT_DATE)
    assert result.servicer is ServicerId.MRC
    assert result.remit_date == REMIT_DATE
    assert list(result.df.columns) == list(REMIT_SUMMARY_COLUMNS) + [ASOFDATE]
    assert (result.df[ASOFDATE] == REMIT_DATE).all()
    # 13 sum aliases per mrc_validation.py:13-27.
    assert len(REMIT_SUMMARY_COLUMNS) == 13


# ---------------------------------------------------------------------------
# Case 2 — RemitSummary rejects missing columns
# ---------------------------------------------------------------------------

def test_prepare_remit_summary_missing_column_raises() -> None:
    df = _row(REMIT_SUMMARY_COLUMNS).drop(columns=["servicefee"])
    with pytest.raises(ValueError, match="servicefee"):
        prepare_remit_summary(df, REMIT_DATE)


# ---------------------------------------------------------------------------
# Case 3 — AdvanceTable shape
# ---------------------------------------------------------------------------

def test_prepare_advance_table_shape_and_immutability() -> None:
    df = _row(ADVANCE_TABLE_COLUMNS)
    snapshot = df.copy()
    result = prepare_advance_table(df, REMIT_DATE)
    # 26 advance projection columns per servicer_validation_with_portdaily.py:602-627.
    assert len(ADVANCE_TABLE_COLUMNS) == 26
    assert list(result.df.columns) == list(ADVANCE_TABLE_COLUMNS) + [ASOFDATE]
    # Input must not be mutated.
    pd.testing.assert_frame_equal(df, snapshot)
    assert ASOFDATE not in df.columns


# ---------------------------------------------------------------------------
# Case 4 — GeneralCheckInputs shape
# ---------------------------------------------------------------------------

def test_prepare_general_check_inputs_shape() -> None:
    df = _row(GENERAL_CHECK_COLUMNS)
    result = prepare_general_check_inputs(df, REMIT_DATE)
    # 34 general-check projection columns per
    # servicer_validation_with_portdaily.py:654-696.
    assert len(GENERAL_CHECK_COLUMNS) == 34
    assert list(result.df.columns) == list(GENERAL_CHECK_COLUMNS) + [ASOFDATE]
    assert result.df.iloc[0][ASOFDATE] == REMIT_DATE


# ---------------------------------------------------------------------------
# Case 5 — Other check merge + MoM math
# ---------------------------------------------------------------------------

def test_prepare_other_check_mom_computation() -> None:
    curr = DataFrame(
        [
            {"bucket": "escadv", "description": "tax", "transaction_code": "T1", "amt": 200.0},
            {"bucket": "escadv", "description": "ins", "transaction_code": "T2", "amt": 50.0},
        ]
    )
    prev = DataFrame(
        [
            {"bucket": "escadv", "description": "tax", "transaction_code": "T1", "amt": 100.0},
        ]
    )
    result = prepare_other_check(curr, prev, REMIT_DATE)
    assert list(result.df.columns) == list(OTHER_CHECK_COLUMNS)
    row_tax = result.df[result.df["description"] == "tax"].iloc[0]
    row_ins = result.df[result.df["description"] == "ins"].iloc[0]
    # amt_MoM = amt / amt_1m - 1
    assert row_tax["amt_MoM"] == pytest.approx(1.0)
    # No prev match → amt_1m is NaN → amt_MoM is NaN.
    assert pd.isna(row_ins["amt_1m"])
    assert pd.isna(row_ins["amt_MoM"])


# ---------------------------------------------------------------------------
# Case 6 — Other check tolerates empty prev frame (legacy: pre_df.empty path)
# ---------------------------------------------------------------------------

def test_prepare_other_check_empty_prev_frame() -> None:
    curr = DataFrame(
        [
            {"bucket": "recovcorpadv", "description": "fee", "transaction_code": "C1", "amt": 9.0},
        ]
    )
    prev = DataFrame(columns=["bucket", "description", "transaction_code", "amt"])
    result = prepare_other_check(curr, prev, REMIT_DATE)
    assert len(result.df) == 1
    assert pd.isna(result.df.iloc[0]["amt_1m"])


# ---------------------------------------------------------------------------
# Case 7 — Extra input columns are dropped (only projection survives)
# ---------------------------------------------------------------------------

def test_prepare_advance_table_drops_extra_columns() -> None:
    df = _row(ADVANCE_TABLE_COLUMNS)
    df["unexpected_extra"] = "junk"
    result = prepare_advance_table(df, REMIT_DATE)
    assert "unexpected_extra" not in result.df.columns
