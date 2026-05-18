"""V3 — ``mrc_check_adv_balance`` validator (stub wrapper around resolved SQL).

Legacy source: ``flow/remit_validation/mrc_validation.py:39-54``.
Target sheet:  ``MRC_Advance_Check``.
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


VALIDATOR_ID = "mrc_check_adv_balance"
SHEET_ID = "MRC_Advance_Check"
RESOLVED_SQL = "mrc__mrc_adv_validation_0a77567c40d9.sql"


@register_validator(
    id=VALIDATOR_ID,
    servicer="MRC",
    sheet=SHEET_ID,
    description="V3 — per-loan advance/recovery/escrow balance change, remit vs daily.",
    tags=("mrc", "advance", "remit_vs_daily", "stub"),
)
def run(ctx: ValidatorContext) -> ValidatorOutput:
    df = execute_resolved_sql(ctx, RESOLVED_SQL)
    stamped = stamp_asofdate(df, ctx)
    return wrap_output(ctx=ctx, validator_id=VALIDATOR_ID, df=stamped)
