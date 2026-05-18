"""Typed input/output models for the transformation layer.

Aligned with ``docs/stage2/3.0-data-model.en.md`` (servicer discriminator on
every shared model; immutable frames between pipeline stages).

These dataclasses wrap a ``pandas.DataFrame`` together with the servicer and
``remit_date`` so downstream validators can dispatch without re-inspecting
column order. ``expected_columns`` is the contract that
``whitebox.transform.mrc`` enforces against legacy SQL output shapes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from pandas import DataFrame


class ServicerId(str, Enum):
    """Subset of ``ServicerId`` from ``3.0-data-model.en.md`` § 2.1.

    Inheriting ``str`` keeps JSON serialisation predictable.
    """

    MRC = "MRC"
    CARRINGTON = "CARRINGTON"
    SLS = "SLS"


# ---------------------------------------------------------------------------
# Expected output column tuples — derived from legacy SQL projections.
# Each tuple is followed by a citation pointing at the legacy source file so
# anyone editing the column list can re-verify against the truth source.
# ---------------------------------------------------------------------------

# ``mrc_summary_check`` aggregate result.
# Source: PrefectFlow/flow/remit_validation/mrc_validation.py:13-27
REMIT_SUMMARY_COLUMNS: tuple[str, ...] = (
    "principalreceived",
    "interestreceived",
    "escrowadv_chg",
    "corpadvrec_chg",
    "corpadvnonrec_chg",
    "corpadvtotal_chg",
    "servicefee",
    "otherfees",
    "totalservicefee",
    "subremit",
    "totremit",
    "beginningbalance",
    "endingbalance",
)

# ``mrc_adv_validation`` projected columns.
# Source: PrefectFlow/flow/remit_validation/servicer_validation_with_portdaily.py:602-627
ADVANCE_TABLE_COLUMNS: tuple[str, ...] = (
    "loanid",
    "mrc_ln",
    "dealid",
    "delq_status",
    "escrowadv_prev_daily",
    "escrowadv_curr_daily",
    "escrowadv_chg_daily",
    "reccorpadvance_prev_daily",
    "reccorpadvance_curr_daily",
    "nonrecovcorpadv_prev_daily",
    "nonrecovcorpadv_curr_daily",
    "totalcorpadv_prev_daily",
    "totalcorpadv_curr_daily",
    "reccorpadvance_chg_daily",
    "nonrecovcorpadv_chg_daily",
    "totalcorpadv_chg_daily",
    "reccorpadvance_remit",
    "nonrecovadvance_remit",
    "escadv_remit",
    "totalcorpadvance_remit",
    "escadv_diff_remitvsdaily",
    "nonrecovcorpadv_diff_remitvsdaily",
    "recovcorpadv_diff_remitvsdaily",
    "totalcorpadv_diff_remitvsdaily",
    "escrow_balance_prev",
    "escrow_balance_curr",
)

# ``mrc_general_check`` projected columns.
# Source: PrefectFlow/flow/remit_validation/servicer_validation_with_portdaily.py:654-696
GENERAL_CHECK_COLUMNS: tuple[str, ...] = (
    "loanid",
    "mrc_ln",
    "dealid",
    "intrate_remit",
    "nextduedate_remit",
    "begbal_remit",
    "endbal_remit",
    "principal_remit",
    "interest_remit",
    "pandi_remit",
    "deferredprincipal_remit",
    "deferredint_remit",
    "nextduedate_daily",
    "begbal_daily",
    "endbal_daily",
    "deferredprincipal_daily",
    "deferredint_daily",
    "pandiexpected_daily",
    "principalreceived_daily",
    "interestreceived_daily",
    "pandireceived_daily",
    "intrate_daily",
    "delinquency_status_mba",
    "prin_bal_diff_remit",
    "begbal_diff_remitvsdaily",
    "endbal_diff_remitvsdaily",
    "deferredprincipal_diff_remitvsdaily",
    "deferredint_diff_remitvsdaily",
    "intrate_diff_remitvsdaily",
    "nextduedate_diff_remitvsdaily",
    "pandi_diff_remitvsdaily",
    "pandi_schedule_diff_remitvsdaily",
    "pandi_paid_times_remit",
    "pandi_paid_times_daily",
)

# ``mrc_other_check`` merged result.
# Source: PrefectFlow/flow/remit_validation/mrc_validation.py:148-154
OTHER_CHECK_COLUMNS: tuple[str, ...] = (
    "bucket",
    "description",
    "transaction_code",
    "amt",
    "amt_1m",
    "amt_MoM",
)


@dataclass(frozen=True)
class _StampedFrame:
    """Common base — a stamped DataFrame plus servicer/date discriminators."""

    servicer: ServicerId
    remit_date: date
    df: DataFrame
    expected_columns: tuple[str, ...] = field(default=())


@dataclass(frozen=True)
class RemitSummary(_StampedFrame):
    """One-row aggregate frame fed to ``V1 mrc_summary_check`` rendering."""


@dataclass(frozen=True)
class AdvanceTable(_StampedFrame):
    """Per-loan advance check inputs fed to ``V2 mrc_check_adv_balance``."""


@dataclass(frozen=True)
class GeneralCheckInputs(_StampedFrame):
    """Per-loan general check inputs fed to ``V3 mrc_check_general_info``."""


@dataclass(frozen=True)
class OtherCheckTable(_StampedFrame):
    """Bucketed advances frame fed to ``V5 mrc_other_check``."""


__all__ = [
    "ADVANCE_TABLE_COLUMNS",
    "AdvanceTable",
    "GENERAL_CHECK_COLUMNS",
    "GeneralCheckInputs",
    "OTHER_CHECK_COLUMNS",
    "OtherCheckTable",
    "REMIT_SUMMARY_COLUMNS",
    "RemitSummary",
    "ServicerId",
]
