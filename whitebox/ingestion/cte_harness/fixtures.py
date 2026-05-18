"""Fixture descriptors for the CTE harness.

A fixture is a small synthetic CSV that simulates a Redshift table.
Files on disk follow the convention ``<schema>__<table>.csv`` so the
schema-qualified Redshift name can be recovered from the filename
(double underscore is the schema/table separator since neither schemas
nor table names contain it in the resolved MRC SQLs).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_SCHEMA_TABLE_SEP = "__"


@dataclass(frozen=True)
class FixtureTable:
    """Single fixture table: a CSV mapped to a schema-qualified name."""

    schema: str
    name: str
    csv_path: Path

    @property
    def qualified_name(self) -> str:
        """Fully-qualified ``schema.table`` identifier."""
        return f"{self.schema}.{self.name}"


@dataclass(frozen=True)
class FixtureSet:
    """Ordered collection of :class:`FixtureTable` to load into DuckDB."""

    tables: tuple[FixtureTable, ...]

    @classmethod
    def from_directory(cls, root: Path) -> FixtureSet:
        """Discover ``<schema>__<table>.csv`` files under ``root``.

        Files not matching the convention are ignored. Order is
        deterministic (sorted by qualified name) so replays are
        reproducible.
        """
        if not root.is_dir():
            raise FileNotFoundError(f"Fixture directory not found: {root}")

        discovered: list[FixtureTable] = []
        for csv in sorted(root.glob("*.csv")):
            stem = csv.stem
            if _SCHEMA_TABLE_SEP not in stem:
                continue
            schema, _, name = stem.partition(_SCHEMA_TABLE_SEP)
            if not schema or not name:
                continue
            discovered.append(FixtureTable(schema=schema, name=name, csv_path=csv))
        return cls(tables=tuple(discovered))

    def qualified_names(self) -> tuple[str, ...]:
        return tuple(t.qualified_name for t in self.tables)
