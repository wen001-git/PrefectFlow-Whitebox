"""V2 — ``mrc_check_general_info`` validator (stub wrapper around resolved SQL).

Legacy source: ``flow/remit_validation/mrc_validation.py:57-72``.
Target sheet:  ``MRC_General_Check``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from whitebox.engine.results import ValidatorOutput
from whitebox.registry import register_validator
from whitebox.validators.mrc._common import (
    execute_resolved_sql,
    stamp_asofdate,
    wrap_output,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from whitebox.engine.pipeline import ValidatorContext


VALIDATOR_ID = "mrc_check_general_info"
SHEET_ID = "MRC_General_Check"
RESOLVED_SQL = "mrc__mrc_general_check_62a675d7e6c6.sql"


@register_validator(
    id=VALIDATOR_ID,
    servicer="MRC",
    sheet=SHEET_ID,
    description="V2 — per-loan remit vs daily reconciliation (rate / next-due / balances).",
    tags=("mrc", "general", "remit_vs_daily", "stub"),
)
def run(ctx: ValidatorContext) -> ValidatorOutput:
    df = execute_resolved_sql(ctx, RESOLVED_SQL)
    stamped = stamp_asofdate(df, ctx)
    return wrap_output(ctx=ctx, validator_id=VALIDATOR_ID, df=stamped)
