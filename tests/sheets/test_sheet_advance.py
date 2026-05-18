"""Tests for ``whitebox.sheets.mrc.sheet_advance``.

Chapter ref: ``docs/mrc/1.3-sheets.en.md`` § 7 (MRC_Advance_Check).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from whitebox.sheets.base import ValidatorOutput
from whitebox.sheets.mrc import sheet_advance

# § 7.1 — 4 highlight columns.
EXPECTED_HIGHLIGHTS = (
    "escadv_diff_remitvsdaily",
    "recovcorpadv_diff_remitvsdaily",
    "nonrecovcorpadv_diff_remitvsdaily",
    "totalcorpadv_diff_remitvsdaily",
)


def _inputs(df: pd.DataFrame) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id="mrc_check_adv_balance",
        servicer="MRC",
        df=df,
        asofdate=date(2026, 4, 30),
    )


def test_empty_input() -> None:
    model = sheet_advance.build(_inputs(pd.DataFrame()))
    assert model.sheet_name == "MRC_Advance_Check"
    assert model.rows == ()
    assert len(model.columns) == 27  # § 7.1 — 27 columns


def test_happy_path_two_rows() -> None:
    df = pd.DataFrame(
        [
            {
                "loanid": "L1", "mrc_ln": "MRC1", "dealid": "D1",
                "delq_status": "Current",
                "escadv_remit": 100.0,
                "escadv_diff_remitvsdaily": 0.0,
                "recovcorpadv_diff_remitvsdaily": 50.25,
            },
            {
                "loanid": "L2", "mrc_ln": "MRC2", "dealid": "D2",
                "delq_status": "30",
                "escadv_remit": 200.0,
                "escadv_diff_remitvsdaily": -5.0,  # abs > 0 → highlight
                "recovcorpadv_diff_remitvsdaily": 0.0,
            },
        ]
    )
    model = sheet_advance.build(_inputs(df))
    assert len(model.rows) == 2

    keys = list(model.column_keys())
    esc_idx = keys.index("escadv_diff_remitvsdaily")
    recov_idx = keys.index("recovcorpadv_diff_remitvsdaily")

    # Row 0
    assert "diff" not in model.rows[0].cells[esc_idx].style.classes
    assert "diff" in model.rows[0].cells[recov_idx].style.classes
    # Row 1 — negative non-zero must highlight (abs > 0).
    assert "diff" in model.rows[1].cells[esc_idx].style.classes
    assert "diff" not in model.rows[1].cells[recov_idx].style.classes


def test_edge_case_missing_columns_fill_none() -> None:
    # § 3 — helper-declared columns missing from validator df → np.nan
    # (here: None) and no highlight (NaN never highlights, § 4.3).
    df = pd.DataFrame([{"loanid": "L1", "mrc_ln": "MRC1", "dealid": "D1"}])
    model = sheet_advance.build(_inputs(df))
    assert len(model.rows) == 1

    keys = list(model.column_keys())
    esc_idx = keys.index("escadv_diff_remitvsdaily")
    # money column missing in df → coerced to 0 (money-int) per § 4.2.
    assert model.rows[0].cells[esc_idx].value == 0
    assert "diff" not in model.rows[0].cells[esc_idx].style.classes


def test_column_presence_matches_chapter_spec() -> None:
    model = sheet_advance.build(_inputs(pd.DataFrame()))
    declared = {c.key for c in model.columns if c.highlight}
    assert declared == set(EXPECTED_HIGHLIGHTS)
    # § 7 gap 3: ``recovcorpadv_diff_*`` (highlighted) coexists with
    # ``reccorpadvance_*`` (non-highlighted source) — preserve verbatim.
    keys = model.column_keys()
    assert "recovcorpadv_diff_remitvsdaily" in keys
    assert "reccorpadvance_remit" in keys
    assert "reccorpadvance_chg_daily" in keys
    # First/last column anchors.
    assert keys[0] == "loanid"
    assert keys[-1] == "asofdate"
