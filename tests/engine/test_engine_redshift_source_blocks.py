"""``RedshiftSource`` must refuse to run until G2a unblocks the env."""

from __future__ import annotations

from pathlib import Path

import pytest

from whitebox.engine import EnvironmentNotConfigured, RedshiftSource


def test_redshift_source_blocks_execute_sql() -> None:
    src = RedshiftSource()
    with pytest.raises(EnvironmentNotConfigured) as exc:
        src.execute_sql(Path("nonexistent.sql"))
    msg = str(exc.value)
    assert "RedshiftSource" in msg
    assert "G2a" in msg or "Redshift" in msg


def test_redshift_source_kind() -> None:
    assert RedshiftSource().kind == "redshift"
