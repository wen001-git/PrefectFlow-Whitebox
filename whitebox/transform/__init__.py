"""Pure DataFrame transformations.

This subpackage owns the ``raw → validator-input`` shaping step in the
Stage 2 architecture (docs/stage2/11.0-architecture.en.md § 3). It performs
**no IO and no side effects**; everything is plain pandas function calls.
"""

from __future__ import annotations

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
from whitebox.transform.mrc import (
    ASOFDATE,
    SERVICER_COL,
    apply_servicer_discriminator,
    prepare_advance_table,
    prepare_general_check_inputs,
    prepare_other_check,
    prepare_remit_summary,
)
from whitebox.transform.pipeline import Transform, compose, identity, pipe

__all__ = [
    "ADVANCE_TABLE_COLUMNS",
    "ASOFDATE",
    "AdvanceTable",
    "GENERAL_CHECK_COLUMNS",
    "GeneralCheckInputs",
    "OTHER_CHECK_COLUMNS",
    "OtherCheckTable",
    "REMIT_SUMMARY_COLUMNS",
    "RemitSummary",
    "SERVICER_COL",
    "ServicerId",
    "Transform",
    "apply_servicer_discriminator",
    "compose",
    "identity",
    "pipe",
    "prepare_advance_table",
    "prepare_general_check_inputs",
    "prepare_other_check",
    "prepare_remit_summary",
]
