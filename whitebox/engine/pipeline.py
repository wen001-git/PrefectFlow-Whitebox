"""The :class:`Engine` class — top-level orchestration entry point.

Engine logic is thin by design: it does no SQL, no rendering, no
business decisions. It owns four steps:

1. **Bootstrap** registries (validators + sheet specs).
2. **Build context** — a :class:`ValidatorContext` carrying the
   discriminators every validator needs.
3. **Run validators** via :func:`whitebox.engine.runner.run_validators`.
4. **Build sheet results** via
   :func:`whitebox.engine.runner.build_sheet_result` and roll them up
   into a :class:`whitebox.engine.results.RunResult`.

Anything substantive lives in transform / registry / sheets / renderer
(``docs/stage2/11.0-architecture.en.md`` § 3).
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from whitebox.engine.results import RunResult, SheetResult
from whitebox.engine.runner import build_sheet_result, run_validators

if TYPE_CHECKING:  # pragma: no cover - typing only
    from whitebox.engine.sources import SourceConfig

__all__ = ["Engine", "ValidatorContext"]


@dataclass(frozen=True)
class ValidatorContext:
    """Per-run context handed to every validator function.

    Validators are pure with respect to this object: they may call
    :meth:`source.execute_sql <whitebox.engine.sources.SourceConfig.execute_sql>`
    but **must not** mutate ``ctx``.

    Fields:
    - ``servicer`` — the ServicerId string (e.g. ``"MRC"``).
    - ``remit_date`` — the logical cycle date for the run (stamped onto
      every output frame so the sheet builders can read it back).
    - ``source`` — the source adapter to execute SQL against.
    - ``extras`` — opaque key/value bag for servicer-specific needs
      (e.g. MRC's ``fctrdt`` / ``fctrdt_1m`` time anchors). Engine
      passes whatever the caller put in; validators look up by key.
    """

    servicer: str
    remit_date: date
    source: SourceConfig
    extras: dict[str, str] = field(default_factory=dict)


class Engine:
    """MRC-aware orchestration engine.

    Construction is cheap; :meth:`run` does the work. Use
    :meth:`bootstrap_mrc` once at app startup to ensure validator +
    sheet registries are populated.
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @classmethod
    def bootstrap_mrc(cls) -> Engine:
        """Build an engine with MRC validators + sheets registered.

        Idempotent — safe to call multiple times in the same process
        (registries silently skip duplicates).
        """
        # Local import avoids a circular dependency at engine package
        # import time (``mrc_wiring`` imports validators which import
        # the registry which … none of this depends on Engine itself).
        from whitebox.engine.mrc_wiring import bootstrap_mrc

        bootstrap_mrc()
        return cls()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        servicer: str,
        remit_date: date,
        source: SourceConfig,
        run_id: str | None = None,
        extras: dict[str, str] | None = None,
    ) -> RunResult:
        """Execute the full pipeline and return a :class:`RunResult`.

        Determinism: when ``run_id`` is ``None`` the engine derives a
        stable id from ``(servicer, remit_date, source.kind)`` so the
        same logical run produces the same id (important for the CLI
        smoke test that renders twice and compares determinism).
        """
        created_at = datetime.now(tz=timezone.utc)
        ctx = ValidatorContext(
            servicer=servicer,
            remit_date=remit_date,
            source=source,
            extras=dict(extras) if extras else {},
        )

        invocations = run_validators(servicer, ctx)
        sheets: tuple[SheetResult, ...] = tuple(
            build_sheet_result(inv) for inv in invocations
        )

        rid = run_id or self._derive_run_id(servicer, remit_date, source.kind)

        metadata: dict[str, str] = {
            "engine_version": "p2.5",
            "validator_count": str(len(invocations)),
            "sheet_count": str(len(sheets)),
        }
        metadata.update(source.describe())

        return RunResult.build(
            run_id=rid,
            servicer=servicer,
            remit_date=remit_date,
            source_kind=source.kind,
            created_at=created_at,
            sheets=sheets,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _derive_run_id(servicer: str, remit_date: date, source_kind: str) -> str:
        """Deterministic id of the form ``run_<servicer>_<date>_<src>_<sha8>``."""
        payload = f"{servicer}|{remit_date.isoformat()}|{source_kind}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
        return f"run_{servicer.lower()}_{remit_date.isoformat()}_{source_kind}_{digest}"

    @staticmethod
    def fresh_run_id() -> str:
        """Random UUID-based run id (escape hatch for non-deterministic callers)."""
        return f"run_{uuid.uuid4().hex[:12]}"
