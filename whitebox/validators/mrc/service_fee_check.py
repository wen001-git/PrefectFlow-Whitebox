"""V4 — ``mrc_service_fee_check`` validator (stub wrapper around resolved SQL).

Legacy source: ``flow/remit_validation/mrc_validation.py:75-102``.
Target sheet:  ``MRC_ServiceFee_Check``.

This is the only MRC validator that the local CTE harness *fully*
runs today (fixtures exist for ``mrc.portmrcremitloanlevelrecap`` /
``port.portfunding`` / ``port.portmonth`` — see
``tests/fixtures/cte_harness/``).
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


VALIDATOR_ID = "mrc_service_fee_check"
SHEET_ID = "MRC_ServiceFee_Check"
RESOLVED_SQL = "mrc__mrc_service_fee_check_86a6badfe1ed.sql"


@register_validator(
    id=VALIDATOR_ID,
    servicer="MRC",
    sheet=SHEET_ID,
    description="V4 — per-loan servicefee diff: portmrcremitloanlevelrecap vs portmonth.",
    tags=("mrc", "service_fee"),
)
def run(ctx: ValidatorContext) -> ValidatorOutput:
    df = execute_resolved_sql(ctx, RESOLVED_SQL)
    stamped = stamp_asofdate(df, ctx)
    return wrap_output(ctx=ctx, validator_id=VALIDATOR_ID, df=stamped)
