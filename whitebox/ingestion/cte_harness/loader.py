"""Load fixture CSVs into a DuckDB connection under their Redshift names."""

from __future__ import annotations

import duckdb

from whitebox.ingestion.cte_harness.fixtures import FixtureSet


def load_fixtures(con: duckdb.DuckDBPyConnection, fixtures: FixtureSet) -> None:
    """Create schemas + tables for every entry in ``fixtures``.

    Each fixture CSV is registered as ``"<schema>"."<table>"`` (the same
    qualified name the resolved MRC SQL refers to), so the SQL runs
    unchanged against the in-memory DuckDB.

    Existing tables with the same name are replaced (idempotent within a
    single connection).
    """
    schemas: set[str] = {t.schema for t in fixtures.tables}
    for schema in sorted(schemas):
        con.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')

    for table in fixtures.tables:
        if not table.csv_path.exists():
            raise FileNotFoundError(
                f"Fixture CSV missing for {table.qualified_name}: {table.csv_path}"
            )
        con.execute(
            f'CREATE OR REPLACE TABLE "{table.schema}"."{table.name}" AS '
            "SELECT * FROM read_csv_auto(?, header=true)",
            [str(table.csv_path)],
        )
