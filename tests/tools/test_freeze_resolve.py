"""Unit tests for tools/freeze_snapshot.py placeholder resolver (G2a A3)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

import pytest
from freeze_snapshot import (  # type: ignore[import]
    _MRC_BUILTIN_BINDINGS,
    _MRC_BUILTIN_FANOUT,
    _apply_bindings,
    _unresolved_placeholders,
    resolve_template,
)

_BINDINGS = _MRC_BUILTIN_BINDINGS
_FANOUT = _MRC_BUILTIN_FANOUT


def test_apply_bindings_fctrdt() -> None:
    sql = "select * from port.portmonth where fctrdt = '{mrc_db.fctrdt}'"
    resolved, used = _apply_bindings(sql, _BINDINGS)
    assert "2026-05-01" in resolved
    assert "{mrc_db.fctrdt}" not in resolved
    assert used.get("mrc_db.fctrdt") == "2026-05-01"


def test_fanout_mrc_adv_info_sql() -> None:
    sql = "select * from mrc.t where fctrdt = '{fctrdt}'"
    variants = resolve_template("_mrc_adv_info_sql", sql, _BINDINGS, _FANOUT)
    assert len(variants) == 2
    suffixes = [v[0] for v in variants]
    resolved_sqls = [v[1] for v in variants]
    assert suffixes[0] != suffixes[1]
    for rsql in resolved_sqls:
        assert "{fctrdt}" not in rsql
        assert _unresolved_placeholders(rsql) == []
    all_dates = {v[1] for v in variants}
    assert any("2026-05-01" in s for s in all_dates)
    assert any("2026-04-01" in s for s in all_dates)


def test_apply_bindings_replace_style() -> None:
    sql = "where fctrdt = 'input_fctrdt' and asofdate = 'input_curr_month_end'"
    resolved, used = _apply_bindings(sql, _BINDINGS)
    assert "input_fctrdt" not in resolved
    assert "input_curr_month_end" not in resolved
    assert "2026-05-01" in resolved
    assert "2026-04-30" in resolved


def test_resolved_sql_no_remaining_placeholders() -> None:
    adv_sql = (
        "select * from mrc.portmrcremit3rdpartyadvances where fctrdt = '{fctrdt}'"
    )
    variants = resolve_template("_mrc_adv_info_sql", adv_sql, _BINDINGS, _FANOUT)
    for _suffix, rsql, _used in variants:
        assert rsql.strip()
        remaining = _unresolved_placeholders(rsql)
        assert remaining == [], f"Unresolved: {remaining}"


def test_unresolved_placeholder_raises() -> None:
    sql = "select * from t where col = '{unknown_placeholder_xyz}'"
    with pytest.raises(ValueError, match="Unresolved"):
        resolve_template("some_function", sql, _BINDINGS, _FANOUT)
