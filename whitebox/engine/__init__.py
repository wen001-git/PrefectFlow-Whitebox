"""Stage 2 P2.5 — MRC validation engine.

This subpackage is the orchestrator: it wires together the
``ingestion`` → ``transform`` → ``validators`` (via the registry) →
``sheets`` → ``renderer`` stages defined in
``docs/stage2/11.0-architecture.en.md`` § 3.

Engine logic is intentionally thin: real work lives in the per-stage
packages. The engine only:

1. Discovers + registers validators + sheet specs (idempotent).
2. Dispatches validators per servicer/sheet via
   :mod:`whitebox.registry`.
3. Routes each :class:`ValidatorOutput` to its sheet builder.
4. Aggregates verdicts and emits a :class:`RunResult` that downstream
   code (CLI, API, renderer) can serialise.

Public API::

    from whitebox.engine import Engine, RunResult, CTEHarnessSource

    engine = Engine.bootstrap_mrc()
    result = engine.run(
        servicer="MRC",
        remit_date=date(2026, 4, 30),
        source=CTEHarnessSource(fixture_dir=...),
    )
"""

from __future__ import annotations

from whitebox.engine.mrc_wiring import (
    MRC_VALIDATOR_IDS,
    bootstrap_mrc,
    register_mrc_validators,
)
from whitebox.engine.pipeline import Engine, ValidatorContext
from whitebox.engine.results import (
    OverallVerdict,
    RunResult,
    SheetResult,
    SheetVerdict,
    ValidatorOutput,
)
from whitebox.engine.runner import dispatch_sheet_builder, run_validators
from whitebox.engine.sources import (
    CTEHarnessSource,
    EnvironmentNotConfigured,
    RedshiftSource,
    SourceConfig,
)

__all__ = [
    "CTEHarnessSource",
    "Engine",
    "EnvironmentNotConfigured",
    "MRC_VALIDATOR_IDS",
    "OverallVerdict",
    "RedshiftSource",
    "RunResult",
    "SheetResult",
    "SheetVerdict",
    "SourceConfig",
    "ValidatorContext",
    "ValidatorOutput",
    "bootstrap_mrc",
    "dispatch_sheet_builder",
    "register_mrc_validators",
    "run_validators",
]
