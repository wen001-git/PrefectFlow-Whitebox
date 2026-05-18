"""Result / verdict dataclasses produced by the engine.

These types are the contract returned by :meth:`Engine.run` and consumed
by the CLI, the API ``engine_backend`` adapter, and tests. They are
deliberately JSON-serialisable via :meth:`RunResult.to_dict`.

``ValidatorOutput`` is re-exported from :mod:`whitebox.sheets.base` —
the engine and the sheet builders **must** agree on the same shape, so
there is exactly one definition.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

from whitebox.sheets.base import SheetModel, ValidatorOutput

__all__ = [
    "OverallVerdict",
    "RunResult",
    "SheetResult",
    "SheetVerdict",
    "ValidatorOutput",
]


class SheetVerdict(str, Enum):
    """Per-sheet verdict.

    The vocabulary mirrors :class:`whitebox.api.schemas.DiffVerdict`
    *intent* but is engine-internal (the engine has no diff baseline at
    this point — it only knows whether highlights fired). Mapping to
    the API verdict is the adapter's job.
    """

    PASS = "PASS"           # validator ran, no highlight cells produced
    WARN = "WARN"           # validator ran, at least one highlight cell
    DEGRADED = "DEGRADED"   # validator could not execute its SQL (stub)
    ERROR = "ERROR"         # uncaught exception inside the validator


class OverallVerdict(str, Enum):
    """Overall run verdict — worst-of the sheet verdicts."""

    PASS = "PASS"
    WARN = "WARN"
    DEGRADED = "DEGRADED"
    ERROR = "ERROR"


# Ordering used by :meth:`RunResult._roll_up`: later entries are "worse".
_VERDICT_RANK: dict[str, int] = {
    SheetVerdict.PASS.value: 0,
    SheetVerdict.WARN.value: 1,
    SheetVerdict.DEGRADED.value: 2,
    SheetVerdict.ERROR.value: 3,
}


@dataclass(frozen=True)
class SheetResult:
    """One sheet's bundle of validator output + sheet model + verdict."""

    sheet_name: str
    validator_id: str
    verdict: SheetVerdict
    row_count: int
    highlight_count: int
    sheet_model: SheetModel
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "sheet_name": self.sheet_name,
            "validator_id": self.validator_id,
            "verdict": self.verdict.value,
            "row_count": self.row_count,
            "highlight_count": self.highlight_count,
            "column_count": len(self.sheet_model.columns),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class RunResult:
    """Top-level engine output for one (servicer, remit_date, source) run."""

    run_id: str
    servicer: str
    remit_date: date
    source_kind: str
    created_at: datetime
    sheets: tuple[SheetResult, ...] = field(default_factory=tuple)
    overall_verdict: OverallVerdict = OverallVerdict.PASS
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def sheet_models(self) -> tuple[SheetModel, ...]:
        return tuple(s.sheet_model for s in self.sheets)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable view (no openpyxl, no pandas frames)."""
        return {
            "run_id": self.run_id,
            "servicer": self.servicer,
            "remit_date": self.remit_date.isoformat(),
            "source_kind": self.source_kind,
            "created_at": self.created_at.isoformat(),
            "overall_verdict": self.overall_verdict.value,
            "sheets": [s.to_dict() for s in self.sheets],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def build(
        cls,
        *,
        run_id: str,
        servicer: str,
        remit_date: date,
        source_kind: str,
        created_at: datetime,
        sheets: tuple[SheetResult, ...],
        metadata: Mapping[str, str] | None = None,
    ) -> RunResult:
        verdict = cls._roll_up(sheets)
        return cls(
            run_id=run_id,
            servicer=servicer,
            remit_date=remit_date,
            source_kind=source_kind,
            created_at=created_at,
            sheets=sheets,
            overall_verdict=verdict,
            metadata=dict(metadata) if metadata else {},
        )

    @staticmethod
    def _roll_up(sheets: tuple[SheetResult, ...]) -> OverallVerdict:
        if not sheets:
            return OverallVerdict.PASS
        worst = max((_VERDICT_RANK[s.verdict.value] for s in sheets), default=0)
        for value, rank in _VERDICT_RANK.items():
            if rank == worst:
                return OverallVerdict(value)
        return OverallVerdict.PASS
