"""CTE harness: DuckDB-based local replay of resolved MRC SQLs.

Allows developers to iterate on CTE / SQL transforms locally without
Redshift access (G2a is environment-blocked). Fixtures are tiny
synthetic CSVs registered into an in-memory DuckDB under their original
schema-qualified Redshift names so the resolved SQL runs unchanged.

Public API:
    - FixtureTable, FixtureSet      (fixtures.py)
    - load_fixtures                 (loader.py)
    - CTEHarnessEngine              (engine.py)
    - MissingFixtureError           (engine.py)
    - replay_sql                    (replay.py)
"""

from whitebox.ingestion.cte_harness.engine import CTEHarnessEngine, MissingFixtureError
from whitebox.ingestion.cte_harness.fixtures import FixtureSet, FixtureTable
from whitebox.ingestion.cte_harness.loader import load_fixtures
from whitebox.ingestion.cte_harness.replay import replay_sql

__all__ = [
    "CTEHarnessEngine",
    "FixtureSet",
    "FixtureTable",
    "MissingFixtureError",
    "load_fixtures",
    "replay_sql",
]
