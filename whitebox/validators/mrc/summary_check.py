"""V1 — ``mrc_summary_check`` validator (stub wrapper around resolved SQL).

Legacy source: ``flow/remit_validation/mrc_validation.py:8-36``.
Target sheet:  ``MRC_Summary_check``.

This is a *stub* in the sense that the heavy lifting lives in the
already-frozen resolved SQL (``mrc__mrc_summary_check_*.sql``); the
Python validator just runs it through the source adapter and stamps
``asofdate``. When the harness is missing the upstream fixture
(``port.portmonth`` with the full 13 sum-aliases) the runner will
catch the resulting :class:`MissingFixtureError` and downgrade the
sheet to ``DEGRADED``.
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


VALIDATOR_ID = "mrc_summary_check"
SHEET_ID = "MRC_Summary_check"
RESOLVED_SQL = "mrc__mrc_summary_check_e943649b57cd.sql"


@register_validator(
    id=VALIDATOR_ID,
    servicer="MRC",
    sheet=SHEET_ID,
    description="V1 — single-row aggregate over port.portmonth for MRC loans.",
    tags=("mrc", "summary", "stub"),
)
def run(ctx: ValidatorContext) -> ValidatorOutput:
    df = execute_resolved_sql(ctx, RESOLVED_SQL)
    stamped = stamp_asofdate(df, ctx)
    return wrap_output(ctx=ctx, validator_id=VALIDATOR_ID, df=stamped)
