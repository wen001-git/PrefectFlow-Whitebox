"""Cell-identity smoke test — render the 5 MRC sheets twice and xlsx_diff.

Per ``docs/stage2/11.0-architecture.en.md`` § 6: until the engine layer
lands, the available evidence for the sheets+renderer chain is a
self-render comparison. The full legacy-vs-new comparison requires real
validator outputs and is deferred to a later P2 todo.

This test exercises the *entire* sheets+renderer path: the 5 MRC sheet
builders feed empty validator outputs into :func:`render_workbook`, the
result is written to disk twice, and ``tools.xlsx_diff.diff_workbooks``
must report exit code ``0`` (identical) on every comparison.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from tools.xlsx_diff import DiffOptions, diff_workbooks
from whitebox.renderer import render_workbook, write_workbook
from whitebox.sheets.base import SheetModel, ValidatorOutput
from whitebox.sheets.mrc import (
    sheet_advance,
    sheet_general_check,
    sheet_other_check,
    sheet_service_fee,
    sheet_summary,
)

_MRC_BUILDERS = (
    sheet_summary,
    sheet_general_check,
    sheet_advance,
    sheet_service_fee,
    sheet_other_check,
)


def _empty_inputs(validator_id: str) -> ValidatorOutput:
    return ValidatorOutput(
        validator_id=validator_id,
        servicer="MRC",
        df=pd.DataFrame(),
        asofdate=date(2026, 4, 30),
    )


def _build_all_mrc_models() -> list[SheetModel]:
    return [mod.build(_empty_inputs(mod.SHEET_NAME)) for mod in _MRC_BUILDERS]


def test_render_all_5_mrc_sheets_with_empty_inputs() -> None:
    models = _build_all_mrc_models()
    assert [m.sheet_name for m in models] == [
        "MRC_Summary_check",
        "MRC_General_Check",
        "MRC_Advance_Check",
        "MRC_ServiceFee_Check",
        "MRC_Adv_Info",
    ]
    wb = render_workbook(models)
    assert wb.sheetnames == [m.sheet_name for m in models]


def test_self_render_cell_identity(tmp_path: Path) -> None:
    """Render twice, diff via tools/xlsx_diff.py, expect ``identical``."""
    models = _build_all_mrc_models()
    a = write_workbook(render_workbook(models), tmp_path / "a.xlsx")
    b = write_workbook(render_workbook(models), tmp_path / "b.xlsx")

    opts = DiffOptions()
    report = diff_workbooks(a, b, opts)

    assert report.major_count == 0, (
        f"unexpected MAJOR diffs: {report.major_count} "
        f"(value/formula/structure/merged_cells)"
    )
    assert report.minor_count == 0, (
        f"unexpected MINOR diffs: {report.minor_count} "
        f"(style/format/freeze/width/sheet_view)"
    )
