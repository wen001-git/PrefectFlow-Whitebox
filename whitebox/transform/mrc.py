"""MRC-specific pure transforms.

Each function takes one or more Redshift-result-shaped DataFrames (i.e. what
the legacy ``mrc_db.run_sql(...)`` calls return) and emits a typed
validator-input model from :mod:`whitebox.transform.models`.

PURITY CONTRACT
---------------
- No IO of any kind (no ``pandas.read_*``, no env, no time, no random).
- Inputs are never mutated; every output DataFrame is freshly constructed via
  ``DataFrame.copy()`` (or built from scratch) so downstream stages cannot
  accidentally observe mutations on the caller's frame.

Shape verification is anchored to legacy source line ranges quoted next to
each helper.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

import pandas as pd
from pandas import DataFrame

from whitebox.transform.models import (
    ADVANCE_TABLE_COLUMNS,
    GENERAL_CHECK_COLUMNS,
    OTHER_CHECK_COLUMNS,
    REMIT_SUMMARY_COLUMNS,
    AdvanceTable,
    GeneralCheckInputs,
    OtherCheckTable,
    RemitSummary,
    ServicerId,
)

ASOFDATE = "asofdate"
SERVICER_COL = "servicer"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _require_columns(df: DataFrame, required: Iterable[str], label: str) -> None:
    """Raise ``ValueError`` if any required column is missing."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"{label}: missing required columns {missing}; got {list(df.columns)}"
        )


def _stamp(df: DataFrame, remit_date: date) -> DataFrame:
    """Return a copy of ``df`` with the ``asofdate`` stamp column appended.

    Mirrors the legacy stamping pattern e.g.
    ``data_df['asofdate'] = mrc_db.remit_date``
    in ``mrc_validation.py:32`` / ``:47`` / ``:65`` / ``:98`` / ``:141``.

    The function is idempotent: stamping an already-stamped frame with the
    same date is a no-op (other than the defensive copy).
    """
    out = df.copy()
    out[ASOFDATE] = remit_date
    return out


# ---------------------------------------------------------------------------
# 1. Summary
# ---------------------------------------------------------------------------

def prepare_remit_summary(df: DataFrame, remit_date: date) -> RemitSummary:
    """Validate + stamp the V1 ``mrc_summary_check`` aggregate.

    Expected ``df`` shape: single row with the 13 ``sum(...)`` aliases listed
    in ``mrc_validation.py:13-27``.
    """
    _require_columns(df, REMIT_SUMMARY_COLUMNS, "prepare_remit_summary")
    stamped = _stamp(df.loc[:, list(REMIT_SUMMARY_COLUMNS)], remit_date)
    return RemitSummary(
        servicer=ServicerId.MRC,
        remit_date=remit_date,
        df=stamped,
        expected_columns=REMIT_SUMMARY_COLUMNS + (ASOFDATE,),
    )


# ---------------------------------------------------------------------------
# 2. Advance check
# ---------------------------------------------------------------------------

def prepare_advance_table(df: DataFrame, remit_date: date) -> AdvanceTable:
    """Validate + stamp the V2 ``mrc_check_adv_balance`` projection.

    Expected ``df`` shape: per-loan columns listed in
    ``servicer_validation_with_portdaily.py:602-627``.
    """
    _require_columns(df, ADVANCE_TABLE_COLUMNS, "prepare_advance_table")
    stamped = _stamp(df.loc[:, list(ADVANCE_TABLE_COLUMNS)], remit_date)
    return AdvanceTable(
        servicer=ServicerId.MRC,
        remit_date=remit_date,
        df=stamped,
        expected_columns=ADVANCE_TABLE_COLUMNS + (ASOFDATE,),
    )


# ---------------------------------------------------------------------------
# 3. General check
# ---------------------------------------------------------------------------

def prepare_general_check_inputs(
    df: DataFrame, remit_date: date
) -> GeneralCheckInputs:
    """Validate + stamp the V3 ``mrc_check_general_info`` projection.

    Expected ``df`` shape: per-loan columns listed in
    ``servicer_validation_with_portdaily.py:654-696``.
    """
    _require_columns(df, GENERAL_CHECK_COLUMNS, "prepare_general_check_inputs")
    stamped = _stamp(df.loc[:, list(GENERAL_CHECK_COLUMNS)], remit_date)
    return GeneralCheckInputs(
        servicer=ServicerId.MRC,
        remit_date=remit_date,
        df=stamped,
        expected_columns=GENERAL_CHECK_COLUMNS + (ASOFDATE,),
    )


# ---------------------------------------------------------------------------
# 4. Other check (bonus — non-trivial merge logic)
# ---------------------------------------------------------------------------

def prepare_other_check(
    curr_df: DataFrame, prev_df: DataFrame, remit_date: date
) -> OtherCheckTable:
    """Merge current/prior advance buckets and compute MoM ratio.

    Reproduces the legacy logic at ``mrc_validation.py:140-154``:

        merged_df = pd.merge(curr_df, pre_df, on=[bucket, description,
                             transaction_code], how='left')
        merged_df['amt_MoM'] = merged_df['amt'] / merged_df['amt_1m'] - 1

    ``curr_df`` carries the ``amt`` column; ``prev_df`` carries ``amt`` which
    is renamed to ``amt_1m`` before the merge. If ``prev_df`` is empty an
    empty frame with the canonical columns is used (see
    ``mrc_validation.py:144-145``).
    """
    base_cols = ("bucket", "description", "transaction_code", "amt")
    _require_columns(curr_df, base_cols, "prepare_other_check[curr_df]")
    if prev_df.empty:
        prev = DataFrame(columns=list(base_cols))
    else:
        _require_columns(prev_df, base_cols, "prepare_other_check[prev_df]")
        prev = prev_df.loc[:, list(base_cols)].copy()
    prev = prev.rename(columns={"amt": "amt_1m"})
    merged = pd.merge(
        curr_df.loc[:, list(base_cols)].copy(),
        prev,
        on=["bucket", "description", "transaction_code"],
        how="left",
    )
    merged["amt_MoM"] = merged["amt"] / merged["amt_1m"] - 1
    merged = merged.loc[:, list(OTHER_CHECK_COLUMNS)]
    return OtherCheckTable(
        servicer=ServicerId.MRC,
        remit_date=remit_date,
        df=merged,
        expected_columns=OTHER_CHECK_COLUMNS,
    )


# ---------------------------------------------------------------------------
# 5. Servicer discriminator
# ---------------------------------------------------------------------------

def apply_servicer_discriminator(
    df: DataFrame, servicer: ServicerId
) -> DataFrame:
    """Filter ``df`` to rows belonging to ``servicer`` and normalise the column.

    Behaviour (mirrors the ``where servicer = 'MRC'`` filter used throughout
    ``servicer_validation_with_portdaily.py``):

    - If a ``servicer`` column exists, rows are filtered to those equal to
      ``servicer.value`` and the column is normalised to that exact string.
    - If the column is absent, the caller's frame is assumed already filtered
      and the column is added (filled with ``servicer.value``) so downstream
      consumers always see a discriminator.

    The function never mutates ``df``; a copy is returned. It is idempotent
    when applied repeatedly with the same ``servicer`` value.
    """
    if not isinstance(servicer, ServicerId):
        raise TypeError(f"servicer must be ServicerId, got {type(servicer).__name__}")
    out = df.copy()
    if SERVICER_COL in out.columns:
        out = out.loc[out[SERVICER_COL].astype(str) == servicer.value].copy()
    out[SERVICER_COL] = servicer.value
    return out.reset_index(drop=True)


__all__ = [
    "ASOFDATE",
    "SERVICER_COL",
    "apply_servicer_discriminator",
    "prepare_advance_table",
    "prepare_general_check_inputs",
    "prepare_other_check",
    "prepare_remit_summary",
]
