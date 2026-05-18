"""Tests for ``whitebox.sheets.mrc.sheet_general_check``.

Chapter ref: ``docs/mrc/1.3-sheets.en.md`` § 6 (MRC_General_Check).
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from whitebox.sheets.base import ValidatorOutput
from whitebox.sheets.mrc import sheet_general_check

# § 6.1 — 7 highlight columns.
EXPECTED_HIGHLIGHTS = (
    "intrate_diff_remitvsdaily",
    "nextduedate_diff_remitvsdaily",
    "begbal_diff_remitvsdaily",
    "endbal_diff_remitvsdaily",
    "deferredprincipal_diff_remitvsdaily",
    "deferredint_diff_remitvsdaily",
    "pandi_schedule_diff_remitvsdaily",
)

# § 6.1 first 3 + last column anchors used to verify ordering.
EXPECTED_FIRST_THREE = ("loanid", "mrc_ln", "dealid")
EXPECTED_LAST = "asofdate"


def _inputs(df: pd.DataFrame) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id="mrc_check_general_info",
        servicer="MRC",
        df=df,
        asofdate=date(2026, 4, 30),
    )


def test_empty_input_yields_zero_rows_but_all_columns() -> None:
    model = sheet_general_check.build(_inputs(pd.DataFrame()))
    assert model.sheet_name == "MRC_General_Check"
    assert model.rows == ()
    assert len(model.columns) == 35  # § 6.1 — 35 columns
    assert model.highlight_keys() == EXPECTED_HIGHLIGHTS


def test_happy_path_three_rows_with_mixed_diffs() -> None:
    df = pd.DataFrame(
        [
            {
                "loanid": "L1", "mrc_ln": "MRC1", "dealid": "D1",
                "intrate_remit": 5.0, "intrate_daily": 5.0,
                "intrate_diff_remitvsdaily": 0.0,
                "begbal_remit": 1000.0, "begbal_daily": 1000.0,
                "begbal_diff_remitvsdaily": 0.0,
            },
            {
                "loanid": "L2", "mrc_ln": "MRC2", "dealid": "D2",
                "intrate_remit": 4.5, "intrate_daily": 4.0,
                "intrate_diff_remitvsdaily": 0.5,  # NON-ZERO → highlight
                "begbal_remit": 2000.0, "begbal_daily": 2000.0,
                "begbal_diff_remitvsdaily": 0.0,
            },
            {
                "loanid": "L3", "mrc_ln": "MRC3", "dealid": "D3",
                "intrate_remit": 3.0, "intrate_daily": 3.0,
                "intrate_diff_remitvsdaily": 0.0,
                "begbal_remit": 3000.0, "begbal_daily": 2999.99,
                "begbal_diff_remitvsdaily": 0.01,  # NON-ZERO → highlight
            },
        ]
    )
    model = sheet_general_check.build(_inputs(df))
    assert len(model.rows) == 3

    # Locate column positions for the two diff fields we care about.
    keys = list(model.column_keys())
    intrate_idx = keys.index("intrate_diff_remitvsdaily")
    begbal_idx = keys.index("begbal_diff_remitvsdaily")

    # Row 0: both diffs zero → no "diff" class.
    assert "diff" not in model.rows[0].cells[intrate_idx].style.classes
    assert "diff" not in model.rows[0].cells[begbal_idx].style.classes
    # Row 1: intrate diff non-zero → "diff" class present.
    assert "diff" in model.rows[1].cells[intrate_idx].style.classes
    assert "diff" not in model.rows[1].cells[begbal_idx].style.classes
    # Row 2: begbal diff non-zero → "diff" class present.
    assert "diff" not in model.rows[2].cells[intrate_idx].style.classes
    assert "diff" in model.rows[2].cells[begbal_idx].style.classes
    # Rounding contract: begbal_diff stays at 0.01 after round(2).
    assert model.rows[2].cells[begbal_idx].value == pytest.approx(0.01)


def test_edge_case_nan_diff_does_not_highlight() -> None:
    # § 4.3 — pd.to_numeric(errors='coerce') means NaN never highlights.
    df = pd.DataFrame(
        [
            {
                "loanid": "L1", "mrc_ln": "MRC1", "dealid": "D1",
                "intrate_diff_remitvsdaily": float("nan"),
                "begbal_diff_remitvsdaily": 0.0,
                # pandi_diff_remitvsdaily must NOT highlight (§ 6 gap 1)
                # even when non-zero.
                "pandi_diff_remitvsdaily": 1234.56,
            }
        ]
    )
    model = sheet_general_check.build(_inputs(df))
    keys = list(model.column_keys())
    intrate_idx = keys.index("intrate_diff_remitvsdaily")
    pandi_idx = keys.index("pandi_diff_remitvsdaily")

    row = model.rows[0]
    assert "diff" not in row.cells[intrate_idx].style.classes  # NaN → no highlight
    assert "diff" not in row.cells[pandi_idx].style.classes    # gap 1: not flagged


def test_column_presence_matches_chapter_spec() -> None:
    model = sheet_general_check.build(_inputs(pd.DataFrame()))
    keys = model.column_keys()
    assert keys[:3] == EXPECTED_FIRST_THREE
    assert keys[-1] == EXPECTED_LAST
    # Every highlight column from § 6.1 is declared and marked.
    declared = {c.key for c in model.columns if c.highlight}
    assert declared == set(EXPECTED_HIGHLIGHTS)
    # gap 1: pandi_diff_remitvsdaily must be present but NOT highlighted.
    pandi = next(c for c in model.columns if c.key == "pandi_diff_remitvsdaily")
    assert pandi.highlight is False
