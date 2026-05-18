"""Orchestration helpers used by :class:`whitebox.engine.pipeline.Engine`.

Two responsibilities live here:

1. :func:`run_validators` — iterate the registered validators for a
   servicer (sorted by sheet ``tab_order``), invoke each with a shared
   :class:`ValidatorContext`, and collect the resulting
   :class:`ValidatorOutput` objects + any per-validator notes.

2. :func:`dispatch_sheet_builder` — given a sheet id, return the
   ``build`` callable from the matching ``whitebox.sheets.<servicer>``
   module. Wired explicitly via :data:`SHEET_BUILDERS` so the engine
   needs no servicer ``if/else`` branches.

Both helpers are pure (no IO except whatever the validator/source do)
and side-effect free, so they are safe to call from tests in any order.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

from whitebox.engine.results import SheetResult, SheetVerdict, ValidatorOutput
from whitebox.registry import (
    UnknownEntryError,
    ValidatorSpec,
    sheet_registry,
    validator_registry,
)
from whitebox.sheets.base import SheetModel
from whitebox.sheets.mrc import (
    sheet_advance,
    sheet_general_check,
    sheet_other_check,
    sheet_service_fee,
    sheet_summary,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from whitebox.engine.pipeline import ValidatorContext

__all__ = [
    "SHEET_BUILDERS",
    "SheetBuilder",
    "ValidatorInvocation",
    "build_sheet_result",
    "dispatch_sheet_builder",
    "run_validators",
]


SheetBuilder = Callable[[ValidatorOutput], SheetModel]


# Explicit sheet → builder map. The engine never imports per-servicer
# sheet modules directly; new servicers extend this dict (or, longer
# term, register a builder via the registry alongside the SheetSpec).
SHEET_BUILDERS: dict[str, SheetBuilder] = {
    sheet_summary.SHEET_NAME: sheet_summary.build,
    sheet_general_check.SHEET_NAME: sheet_general_check.build,
    sheet_advance.SHEET_NAME: sheet_advance.build,
    sheet_service_fee.SHEET_NAME: sheet_service_fee.build,
    sheet_other_check.SHEET_NAME: sheet_other_check.build,
}


def dispatch_sheet_builder(sheet_id: str) -> SheetBuilder:
    """Return the builder registered for ``sheet_id``.

    Raises :class:`KeyError` with a helpful message when the sheet is
    not wired — the engine surfaces this as a hard failure (a misnamed
    validator wiring is a bug, not a degraded run).
    """
    try:
        return SHEET_BUILDERS[sheet_id]
    except KeyError as exc:
        raise KeyError(
            f"No sheet builder registered for sheet_id={sheet_id!r}. "
            f"Known sheets: {sorted(SHEET_BUILDERS)}"
        ) from exc


@dataclass(frozen=True)
class ValidatorInvocation:
    """Result of running one validator: output + provenance notes."""

    spec: ValidatorSpec
    output: ValidatorOutput
    verdict: SheetVerdict
    notes: tuple[str, ...] = ()


def run_validators(
    servicer: str,
    ctx: ValidatorContext,
) -> list[ValidatorInvocation]:
    """Run every registered validator for ``servicer`` and collect outputs.

    Validators are ordered by the ``tab_order`` of their target sheet
    (so the engine renders sheets in their final XLSX tab order). When
    a validator raises:

    - :class:`whitebox.ingestion.cte_harness.MissingFixtureError` or
      :class:`FileNotFoundError` → verdict ``DEGRADED`` (stub fallback).
    - Anything else → verdict ``ERROR`` (re-raises caught here as a
      ``notes`` entry so a single bad validator doesn't poison the run).
    """
    # Local import to avoid a cycle (engine package ↔ ingestion).
    from whitebox.ingestion.cte_harness import MissingFixtureError

    # DuckDB raises BinderException / CatalogException when a fixture
    # CSV is present but its schema doesn't match the resolved SQL —
    # equivalent to "missing fixture data" for the purposes of the
    # stub validators, so treat it the same as MissingFixtureError.
    try:
        import duckdb as _duckdb

        _duckdb_error: type[BaseException] = _duckdb.Error
    except ImportError:  # pragma: no cover - duckdb is a hard dep
        _duckdb_error = type("_NoDuckDB", (Exception,), {})

    specs = validator_registry.by_servicer(servicer)
    ordered = sorted(specs, key=lambda s: _tab_order_for(s.sheet))

    invocations: list[ValidatorInvocation] = []
    for spec in ordered:
        try:
            output = spec.fn(ctx)
        except (MissingFixtureError, FileNotFoundError, _duckdb_error) as exc:
            output = ValidatorOutput(
                validator_id=spec.id,
                servicer=spec.servicer,
                df=_empty_df(),
                asofdate=ctx.remit_date,
            )
            invocations.append(
                ValidatorInvocation(
                    spec=spec,
                    output=output,
                    verdict=SheetVerdict.DEGRADED,
                    notes=(f"degraded: {type(exc).__name__}: {exc}",),
                )
            )
            continue
        except Exception as exc:  # noqa: BLE001 — engine isolates per-validator errors
            output = ValidatorOutput(
                validator_id=spec.id,
                servicer=spec.servicer,
                df=_empty_df(),
                asofdate=ctx.remit_date,
            )
            invocations.append(
                ValidatorInvocation(
                    spec=spec,
                    output=output,
                    verdict=SheetVerdict.ERROR,
                    notes=(f"error: {type(exc).__name__}: {exc}",),
                )
            )
            continue

        if not isinstance(output, ValidatorOutput):
            raise TypeError(
                f"validator {spec.id!r} must return ValidatorOutput, "
                f"got {type(output).__name__}"
            )
        invocations.append(
            ValidatorInvocation(
                spec=spec,
                output=output,
                verdict=SheetVerdict.PASS,
                notes=(),
            )
        )

    return invocations


def build_sheet_result(invocation: ValidatorInvocation) -> SheetResult:
    """Run the sheet builder for ``invocation`` and wrap the result."""
    builder = dispatch_sheet_builder(invocation.spec.sheet)
    model = builder(invocation.output)
    highlight_count = _count_highlight_cells(model)

    # If the validator ran cleanly but produced highlight cells, that
    # is a per-sheet WARN, not PASS. DEGRADED / ERROR verdicts are
    # never upgraded back to WARN even if their empty frames happen to
    # have zero highlights.
    verdict = invocation.verdict
    if verdict is SheetVerdict.PASS and highlight_count > 0:
        verdict = SheetVerdict.WARN

    return SheetResult(
        sheet_name=invocation.spec.sheet,
        validator_id=invocation.spec.id,
        verdict=verdict,
        row_count=len(model.rows),
        highlight_count=highlight_count,
        sheet_model=model,
        notes=invocation.notes,
    )


def _count_highlight_cells(model: SheetModel) -> int:
    n = 0
    for row in model.rows:
        for cell in row.cells:
            if "diff" in cell.style.classes:
                n += 1
    return n


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame()


def _tab_order_for(sheet_id: str) -> int:
    try:
        spec = sheet_registry.get(sheet_id)
    except UnknownEntryError:
        return 9999
    return spec.tab_order
