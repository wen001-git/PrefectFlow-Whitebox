"""Tests for whitebox.ingestion.cte_harness (P2.1)."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from whitebox.ingestion.cte_harness import (
    CTEHarnessEngine,
    FixtureSet,
    MissingFixtureError,
    load_fixtures,
    replay_sql,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "cte_harness"
RESOLVED_SQL_DIR = (
    Path(__file__).resolve().parents[2]
    / "baselines"
    / "mrc"
    / "2026-04-30"
    / "input_snapshots"
    / "_export_queries"
    / "resolved"
)
SMOKE_SQL = RESOLVED_SQL_DIR / "mrc__mrc_service_fee_check_86a6badfe1ed.sql"


def _full_fixtures() -> FixtureSet:
    return FixtureSet.from_directory(FIXTURE_DIR)


def test_load_fixtures() -> None:
    fixtures = _full_fixtures()
    assert {t.qualified_name for t in fixtures.tables} == {
        "mrc.portmrcremitloanlevelrecap",
        "port.portmonth",
        "port.portfunding",
    }

    con = duckdb.connect(":memory:")
    try:
        load_fixtures(con, fixtures)
        n_recap = con.execute("SELECT COUNT(*) FROM mrc.portmrcremitloanlevelrecap").fetchone()
        n_month = con.execute("SELECT COUNT(*) FROM port.portmonth").fetchone()
        n_fund = con.execute("SELECT COUNT(*) FROM port.portfunding").fetchone()
        assert n_recap is not None and n_recap[0] == 6
        assert n_month is not None and n_month[0] == 6
        assert n_fund is not None and n_fund[0] == 4
    finally:
        con.close()


def test_replay_simple_sql() -> None:
    df = replay_sql(SMOKE_SQL, _full_fixtures())
    assert not df.empty
    expected_cols = {
        "fctrdt",
        "loanid",
        "mrc_ln",
        "dealid",
        "servicefee_remit_raw",
        "servicefee_portmonth",
        "servicefee_diff",
    }
    assert expected_cols.issubset(set(df.columns))


def test_replay_with_filters() -> None:
    """The chosen SQL filters ``r.fctrdt = '2026-05-01'`` — the
    2026-04-01 rows must be excluded."""
    df = replay_sql(SMOKE_SQL, _full_fixtures())
    # DuckDB infers fctrdt as DATE/Timestamp; normalise to ISO date prefix.
    fctrdts = {str(v)[:10] for v in df["fctrdt"].tolist()}
    assert fctrdts == {"2026-05-01"}
    assert set(df["loanid"].tolist()) == {"L001", "L002", "L003", "L006"}


def test_missing_fixture_error() -> None:
    """SQL referring to an unloaded schema/table raises a clear error."""
    empty = FixtureSet(tables=())
    with CTEHarnessEngine() as engine:
        engine.load(empty)
        with pytest.raises(MissingFixtureError):
            engine.execute("SELECT * FROM mrc.portmrcremitloanlevelrecap")


def test_isolation(tmp_path: Path) -> None:
    """Two replays through ``replay_sql`` must not share state."""
    # Subset fixture set: only one row in recap (different from full set)
    subset_dir = tmp_path / "subset"
    subset_dir.mkdir()
    (subset_dir / "mrc__portmrcremitloanlevelrecap.csv").write_text(
        "fctrdt,loanid,mrc_ln,total_accrued_earned_servicing_fees\n"
        "2026-05-01,L001,MRC-1,100.50\n",
        encoding="utf-8",
    )
    (subset_dir / "port__portmonth.csv").write_text(
        "fctrdt,loanid,servicer,dealid,servicefee\n"
        "2026-05-01,L001,MRC,D-100,90.00\n",
        encoding="utf-8",
    )
    (subset_dir / "port__portfunding.csv").write_text(
        "loanid,dealid\nL001,DF-001\n",
        encoding="utf-8",
    )

    df_full = replay_sql(SMOKE_SQL, _full_fixtures())
    df_subset = replay_sql(SMOKE_SQL, FixtureSet.from_directory(subset_dir))
    df_full_again = replay_sql(SMOKE_SQL, _full_fixtures())

    assert len(df_subset) == 1
    assert len(df_full) == 4
    assert len(df_full_again) == 4  # not contaminated by the subset replay
