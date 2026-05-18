"""Shared helpers used by every MRC validator stub.

These helpers keep each validator module tiny: just a SQL filename, a
sheet binding, and a one-line ``run`` body.

Each validator wraps a *resolved* SQL file under
``baselines/mrc/2026-04-30/input_snapshots/_export_queries/resolved/``.
The resolved SQL is the cell-identical contract; the engine runs it
verbatim through the source adapter and stamps the result with
``asofdate``.

Behaviour when a resolved SQL cannot run (missing fixture, missing
file, …): the runner catches the resulting exception, marks the sheet
``DEGRADED`` (per
:class:`whitebox.engine.results.SheetVerdict`), and continues — so a
single missing fixture does not abort the whole run.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from whitebox.engine.results import ValidatorOutput
from whitebox.transform.models import ServicerId
from whitebox.transform.mrc import ASOFDATE

if TYPE_CHECKING:  # pragma: no cover - typing only
    from whitebox.engine.pipeline import ValidatorContext

__all__ = [
    "RESOLVED_SQL_DIR",
    "execute_resolved_sql",
    "stamp_asofdate",
    "wrap_output",
]


# Repo-relative location of the cell-identical resolved SQL bundle.
# Discovered at import time from the source-file location so the
# validators work regardless of cwd.
_REPO_ROOT = Path(__file__).resolve().parents[3]
RESOLVED_SQL_DIR: Path = (
    _REPO_ROOT
    / "baselines"
    / "mrc"
    / "2026-04-30"
    / "input_snapshots"
    / "_export_queries"
    / "resolved"
)


def execute_resolved_sql(ctx: ValidatorContext, sql_filename: str) -> pd.DataFrame:
    """Execute one resolved-SQL file via the run's source adapter."""
    sql_path = RESOLVED_SQL_DIR / sql_filename
    return ctx.source.execute_sql(sql_path)


def stamp_asofdate(df: pd.DataFrame, ctx: ValidatorContext) -> pd.DataFrame:
    """Mirror the legacy ``data_df['asofdate'] = mrc_db.remit_date`` step."""
    out = df.copy()
    out[ASOFDATE] = ctx.remit_date
    return out


def wrap_output(
    *,
    ctx: ValidatorContext,
    validator_id: str,
    df: pd.DataFrame,
) -> ValidatorOutput:
    """Standardise the (df, servicer, asofdate) packaging for sheet builders."""
    # Engine ships ``servicer`` as a string; the typed enum lives in
    # the transform layer. Validators don't currently dispatch on the
    # enum so we pass the raw string straight through.
    _ = ServicerId  # keep import — referenced for doc + future use
    return ValidatorOutput(
        validator_id=validator_id,
        servicer=ctx.servicer,
        df=df,
        asofdate=ctx.remit_date,
    )
