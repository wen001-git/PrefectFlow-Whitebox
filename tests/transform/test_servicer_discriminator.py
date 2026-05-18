"""Servicer discriminator filtering semantics."""

from __future__ import annotations

import pytest
from pandas import DataFrame

from whitebox.transform import SERVICER_COL, ServicerId, apply_servicer_discriminator


def _mixed_df() -> DataFrame:
    return DataFrame(
        [
            {"loanid": "a", "servicer": "MRC", "x": 1},
            {"loanid": "b", "servicer": "CARRINGTON", "x": 2},
            {"loanid": "c", "servicer": "SLS", "x": 3},
            {"loanid": "d", "servicer": "MRC", "x": 4},
        ]
    )


def test_filter_mrc_only() -> None:
    out = apply_servicer_discriminator(_mixed_df(), ServicerId.MRC)
    assert list(out["loanid"]) == ["a", "d"]
    assert set(out[SERVICER_COL]) == {"MRC"}


def test_filter_carrington_only() -> None:
    out = apply_servicer_discriminator(_mixed_df(), ServicerId.CARRINGTON)
    assert list(out["loanid"]) == ["b"]
    assert set(out[SERVICER_COL]) == {"CARRINGTON"}


def test_filter_sls_only() -> None:
    out = apply_servicer_discriminator(_mixed_df(), ServicerId.SLS)
    assert list(out["loanid"]) == ["c"]
    assert set(out[SERVICER_COL]) == {"SLS"}


def test_idempotent_when_reapplied() -> None:
    once = apply_servicer_discriminator(_mixed_df(), ServicerId.MRC)
    twice = apply_servicer_discriminator(once, ServicerId.MRC)
    assert list(once["loanid"]) == list(twice["loanid"])
    assert list(once.columns) == list(twice.columns)


def test_adds_column_when_missing() -> None:
    df = DataFrame([{"loanid": "a"}, {"loanid": "b"}])
    out = apply_servicer_discriminator(df, ServicerId.MRC)
    assert SERVICER_COL in out.columns
    assert set(out[SERVICER_COL]) == {"MRC"}
    assert len(out) == 2


def test_input_not_mutated() -> None:
    df = _mixed_df()
    cols_before = list(df.columns)
    rows_before = len(df)
    apply_servicer_discriminator(df, ServicerId.MRC)
    assert list(df.columns) == cols_before
    assert len(df) == rows_before


def test_rejects_non_enum() -> None:
    with pytest.raises(TypeError):
        apply_servicer_discriminator(_mixed_df(), "MRC")  # type: ignore[arg-type]


def test_returns_empty_for_unrepresented_servicer() -> None:
    df = DataFrame([{"loanid": "a", "servicer": "MRC"}])
    out = apply_servicer_discriminator(df, ServicerId.SLS)
    assert len(out) == 0
    assert SERVICER_COL in out.columns
