"""MRC sheet builders (5 sheets, P2.2).

Each ``sheet_*`` module exposes a ``build(inputs: ValidatorOutput) ->
SheetModel`` function. The 5 sheet specs are registered with
``whitebox.registry.sheet_registry`` via :func:`register_mrc_sheets`.

Chapter cross-reference: ``docs/mrc/1.3-sheets.en.md`` (sheet names,
column orders, highlight columns) and ``docs/mrc/1.0-toc.en.md`` § 4
(authoritative sheet-name list).
"""

from __future__ import annotations

from whitebox.registry import DuplicateRegistrationError, register_sheet
from whitebox.sheets.mrc import (
    sheet_advance,
    sheet_general_check,
    sheet_other_check,
    sheet_service_fee,
    sheet_summary,
)

# Authoritative sheet-name list (1.0-toc.en.md § 4 — XLSX tab order).
MRC_SHEET_IDS: tuple[str, ...] = (
    sheet_summary.SHEET_NAME,
    sheet_general_check.SHEET_NAME,
    sheet_advance.SHEET_NAME,
    sheet_service_fee.SHEET_NAME,
    sheet_other_check.SHEET_NAME,
)

_MODULES = (
    sheet_summary,
    sheet_general_check,
    sheet_advance,
    sheet_service_fee,
    sheet_other_check,
)


def register_mrc_sheets(*, override: bool = False) -> None:
    """Register all 5 MRC sheet specs with ``sheet_registry``.

    Idempotent: if a spec is already registered and ``override`` is
    False, the duplicate is silently skipped (test isolation friendly).
    """
    for mod in _MODULES:
        try:
            register_sheet(
                id=mod.SHEET_NAME,
                servicer=mod.SERVICER,
                title=mod.SHEET_NAME,
                tab_order=mod.TAB_ORDER,
                column_count=len(mod.COLUMNS),
                override=override,
            )
        except DuplicateRegistrationError:
            if override:
                raise


__all__ = [
    "MRC_SHEET_IDS",
    "register_mrc_sheets",
    "sheet_advance",
    "sheet_general_check",
    "sheet_other_check",
    "sheet_service_fee",
    "sheet_summary",
]
