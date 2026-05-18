"""DuckDB-backed SQL executor for the CTE harness."""

from __future__ import annotations

from types import TracebackType
from typing import Any

import duckdb
import pandas as pd

from whitebox.ingestion.cte_harness.fixtures import FixtureSet
from whitebox.ingestion.cte_harness.loader import load_fixtures


class MissingFixtureError(RuntimeError):
    """Raised when a SQL references a table not loaded into the harness."""


class CTEHarnessEngine:
    """In-memory DuckDB engine that runs resolved MRC SQLs locally.

    Each engine instance owns a fresh ``:memory:`` connection — there is
    no shared global state between engines, which keeps replays
    isolated.
    """

    def __init__(self) -> None:
        self._con: duckdb.DuckDBPyConnection = duckdb.connect(":memory:")
        self._closed: bool = False

    def load(self, fixtures: FixtureSet) -> None:
        """Register every fixture in ``fixtures`` as a DuckDB table."""
        self._ensure_open()
        load_fixtures(self._con, fixtures)

    def execute(self, sql: str) -> pd.DataFrame:
        """Execute ``sql`` and return the result as a pandas DataFrame.

        A :class:`MissingFixtureError` is raised when the SQL references
        a table (or schema) that has not been loaded — this is the most
        common harness mistake and deserves a clear error.
        """
        self._ensure_open()
        try:
            result: Any = self._con.execute(sql).fetch_df()
        except duckdb.CatalogException as exc:
            raise MissingFixtureError(
                f"SQL references an unloaded fixture (DuckDB catalog miss): {exc}"
            ) from exc
        return result

    def close(self) -> None:
        if not self._closed:
            self._con.close()
            self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("CTEHarnessEngine is closed")

    def __enter__(self) -> CTEHarnessEngine:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
