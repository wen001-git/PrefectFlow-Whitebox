"""V5 — ``mrc_other_check`` validator (stub wrapper).

Legacy source: ``flow/remit_validation/mrc_validation.py:105-158``.
Target sheet:  ``MRC_Adv_Info``.

Unlike the other validators this one runs **two** resolved SQLs (one
per ``fctrdt``) and does a small pandas merge — reproducing the legacy
``amt_MoM = amt / amt_1m - 1`` computation via
:func:`whitebox.transform.mrc.prepare_other_check`.

If either SQL cannot run, the validator raises ``MissingFixtureError``
and the engine downgrades the sheet to ``DEGRADED``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from whitebox.engine.results import ValidatorOutput
from whitebox.registry import register_validator
from whitebox.transform.mrc import prepare_other_check
from whitebox.validators.mrc._common import execute_resolved_sql, wrap_output

if TYPE_CHECKING:  # pragma: no cover - typing only
    from whitebox.engine.pipeline import ValidatorContext


VALIDATOR_ID = "mrc_other_check"
SHEET_ID = "MRC_Adv_Info"
CURR_SQL = "mrc__mrc_adv_info_sql_2634e9f21449__fctrdt=2026-05-01.sql"
PREV_SQL = "mrc__mrc_adv_info_sql_2634e9f21449__fctrdt=2026-04-01.sql"


@register_validator(
    id=VALIDATOR_ID,
    servicer="MRC",
    sheet=SHEET_ID,
    description="V5 — current + prior month advance buckets with MoM ratio.",
    tags=("mrc", "advance_info", "stub"),
)
def run(ctx: ValidatorContext) -> ValidatorOutput:
    curr_df = execute_resolved_sql(ctx, CURR_SQL)
    prev_df = execute_resolved_sql(ctx, PREV_SQL)
    table = prepare_other_check(curr_df, prev_df, ctx.remit_date)
    return wrap_output(ctx=ctx, validator_id=VALIDATOR_ID, df=table.df)
