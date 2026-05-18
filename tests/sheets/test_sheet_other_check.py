"""Tests for ``whitebox.sheets.mrc.sheet_other_check``.

Chapter ref: ``docs/mrc/1.3-sheets.en.md`` § 9 (MRC_Adv_Info).
"""

from __future__ import annotations

import math
from datetime import date

import pandas as pd
import pytest

from whitebox.sheets.base import ValidatorOutput
from whitebox.sheets.mrc import sheet_other_check

EXPECTED_COLUMNS = (
    "bucket",
    "description",
    "transaction_code",
    "amt",
    "amt_1m",
    "amt_MoM",
    "asofdate",
)


def _inputs(df: pd.DataFrame) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id="mrc_other_check",
        servicer="MRC",
        df=df,
        asofdate=date(2026, 4, 30),
    )


def test_empty_input() -> None:
    model = sheet_other_check.build(_inputs(pd.DataFrame()))
    assert model.sheet_name == "MRC_Adv_Info"
    assert model.rows == ()
    assert model.column_keys() == EXPECTED_COLUMNS
    assert model.highlight_keys() == ()  # § 9.1 — no highlights


def test_happy_path_three_rows() -> None:
    df = pd.DataFrame(
        [
            {"bucket": "ADV", "description": "Escrow",
             "transaction_code": "T100",
             "amt": 1000.50, "amt_1m": 800.00, "amt_MoM": 0.25},
            {"bucket": "REC", "description": "Recovery",
             "transaction_code": "T200",
             "amt": 500.00, "amt_1m": 500.00, "amt_MoM": 0.0},
            {"bucket": "DSB", "description": "Disbursement",
             "transaction_code": "T300",
             "amt": 250.75, "amt_1m": 100.25, "amt_MoM": 1.5},
        ]
    )
    model = sheet_other_check.build(_inputs(df))
    assert len(model.rows) == 3
    keys = list(model.column_keys())
    amt_idx = keys.index("amt")
    mom_idx = keys.index("amt_MoM")
    # money styling
    assert "money" in model.rows[0].cells[amt_idx].style.classes
    # float styling — no number_format imposed
    cell = model.rows[0].cells[mom_idx]
    assert "float" in cell.style.classes
    assert cell.value == pytest.approx(0.25)


def test_edge_case_inf_mom_flows_through() -> None:
    # § 9 gap 5: amt_MoM may be ±inf / NaN when amt_1m == 0; the sheet
    # builder must NOT coerce these — they flow through to the renderer.
    df = pd.DataFrame(
        [
            {"bucket": "B1", "description": "d",
             "transaction_code": "T1",
             "amt": 100.0, "amt_1m": 0.0, "amt_MoM": float("inf")},
            {"bucket": "B2", "description": "d",
             "transaction_code": "T2",
             "amt": 0.0, "amt_1m": 0.0, "amt_MoM": float("nan")},
        ]
    )
    model = sheet_other_check.build(_inputs(df))
    keys = list(model.column_keys())
    mom_idx = keys.index("amt_MoM")
    v1 = model.rows[0].cells[mom_idx].value
    v2 = model.rows[1].cells[mom_idx].value
    assert isinstance(v1, float) and math.isinf(v1)
    # NaN → preserved as NaN (renderer + Excel decide final representation).
    assert v2 is None or (isinstance(v2, float) and math.isnan(v2))


def test_column_presence_matches_chapter_spec() -> None:
    model = sheet_other_check.build(_inputs(pd.DataFrame()))
    assert model.column_keys() == EXPECTED_COLUMNS
    # amt + amt_1m are money round 2; amt_MoM is float round 2.
    by_key = {c.key: c for c in model.columns}
    assert by_key["amt"].data_type == "money" and by_key["amt"].round_to == 2
    assert by_key["amt_1m"].data_type == "money" and by_key["amt_1m"].round_to == 2
    assert by_key["amt_MoM"].data_type == "float" and by_key["amt_MoM"].round_to == 2
    assert by_key["asofdate"].data_type == "date"
