"""Public ``replay_sql`` API for the CTE harness."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from whitebox.ingestion.cte_harness.engine import CTEHarnessEngine
from whitebox.ingestion.cte_harness.fixtures import FixtureSet


def replay_sql(sql_path: Path, fixtures: FixtureSet) -> pd.DataFrame:
    """Replay the SQL at ``sql_path`` against local DuckDB ``fixtures``.

    A fresh :class:`CTEHarnessEngine` is created per call, so successive
    replays cannot leak state between each other.
    """
    if not sql_path.is_file():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")
    with CTEHarnessEngine() as engine:
        engine.load(fixtures)
        return engine.execute(sql)
