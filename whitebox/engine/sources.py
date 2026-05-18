"""Engine source adapters — give validators a uniform ``execute_sql`` API.

Two concrete adapters live here:

- :class:`CTEHarnessSource` — local DuckDB replay against fixture CSVs
  (implemented by :mod:`whitebox.ingestion.cte_harness`). Used by the
  CLI smoke run and the engine tests.
- :class:`RedshiftSource` — placeholder that raises
  :class:`EnvironmentNotConfigured` on first use. The real adapter
  lands when the G2a (Redshift access) gate opens.

Any future adapter (S3-backed snapshots, frozen JSON replay, …) only
needs to subclass :class:`SourceConfig`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from whitebox.ingestion.cte_harness import FixtureSet, replay_sql

__all__ = [
    "CTEHarnessSource",
    "EnvironmentNotConfigured",
    "RedshiftSource",
    "SourceConfig",
]


class EnvironmentNotConfigured(RuntimeError):
    """Raised when a source needs an environment that is not available."""


class SourceConfig(ABC):
    """Abstract source adapter.

    Concrete subclasses must implement :meth:`execute_sql` (run a SQL
    file and return a DataFrame) and :attr:`kind` (a stable short tag
    used by :class:`whitebox.engine.results.RunResult` so consumers can
    tell harness runs apart from real-Redshift runs).
    """

    @property
    @abstractmethod
    def kind(self) -> str:
        """Stable short identifier (e.g. ``"cte-harness"``)."""

    @abstractmethod
    def execute_sql(self, sql_path: Path) -> pd.DataFrame:
        """Run the SQL at ``sql_path`` and return a pandas DataFrame."""

    def describe(self) -> Mapping[str, str]:
        """Optional descriptor for ``RunResult.metadata``. Default empty."""
        return {}


@dataclass
class CTEHarnessSource(SourceConfig):
    """Local DuckDB replay backed by ``<schema>__<table>.csv`` fixtures.

    ``fixture_dir`` is loaded once and the resulting
    :class:`whitebox.ingestion.cte_harness.FixtureSet` is cached on the
    instance so subsequent ``execute_sql`` calls don't re-discover the
    CSVs.
    """

    fixture_dir: Path
    _cached_fixtures: FixtureSet | None = field(
        default=None, repr=False, compare=False
    )

    @property
    def kind(self) -> str:
        return "cte-harness"

    def fixtures(self) -> FixtureSet:
        if self._cached_fixtures is None:
            self._cached_fixtures = FixtureSet.from_directory(self.fixture_dir)
        return self._cached_fixtures

    def execute_sql(self, sql_path: Path) -> pd.DataFrame:
        return replay_sql(sql_path, self.fixtures())

    def describe(self) -> Mapping[str, str]:
        return {
            "source_kind": self.kind,
            "fixture_dir": str(self.fixture_dir),
        }


@dataclass(frozen=True)
class RedshiftSource(SourceConfig):
    """Placeholder Redshift source — raises until G2a is unblocked.

    The Stage 2 architecture deliberately keeps Redshift wiring out of
    P2.5 (``docs/stage2/11.0-architecture.en.md`` § 7). Calling
    :meth:`execute_sql` raises :class:`EnvironmentNotConfigured` so the
    CLI / engine fail loudly instead of silently returning empty data.
    """

    cluster: str = ""
    database: str = ""

    @property
    def kind(self) -> str:
        return "redshift"

    def execute_sql(self, sql_path: Path) -> pd.DataFrame:
        raise EnvironmentNotConfigured(
            "RedshiftSource is not wired in this build "
            "(G2a Redshift access is environment-blocked; see "
            "docs/stage2/11.0-architecture.en.md § 7). "
            f"Refused to execute {sql_path}."
        )

    def describe(self) -> Mapping[str, str]:
        return {
            "source_kind": self.kind,
            "cluster": self.cluster,
            "database": self.database,
        }
