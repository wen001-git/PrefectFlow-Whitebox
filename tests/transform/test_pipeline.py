"""Composition + idempotency semantics for the transform pipeline."""

from __future__ import annotations

from datetime import date

import pandas as pd
from pandas import DataFrame

from whitebox.transform import (
    REMIT_SUMMARY_COLUMNS,
    ServicerId,
    apply_servicer_discriminator,
    compose,
    identity,
    pipe,
    prepare_remit_summary,
)

REMIT_DATE = date(2026, 4, 30)


def test_compose_right_to_left() -> None:
    f = compose(lambda x: x + 1, lambda x: x * 2)
    # (x * 2) then + 1
    assert f(3) == 7


def test_pipe_left_to_right() -> None:
    assert pipe(3, lambda x: x * 2, lambda x: x + 1) == 7


def test_empty_compose_is_identity() -> None:
    assert compose()(123) == 123
    assert identity(123) == 123


def test_pipeline_compose_transforms() -> None:
    raw = DataFrame([dict.fromkeys(REMIT_SUMMARY_COLUMNS, 1.0)])
    raw["servicer"] = "MRC"
    # Two-step pipeline: filter → prepare summary.
    pipeline = compose(
        lambda d: prepare_remit_summary(d, REMIT_DATE),
        lambda d: apply_servicer_discriminator(d, ServicerId.MRC),
    )
    result = pipeline(raw)
    assert result.servicer is ServicerId.MRC
    assert (result.df["asofdate"] == REMIT_DATE).all()


def test_servicer_discriminator_idempotent_under_pipe() -> None:
    df = DataFrame(
        [
            {"loanid": "a", "servicer": "MRC"},
            {"loanid": "b", "servicer": "SLS"},
        ]
    )
    once = pipe(df, lambda d: apply_servicer_discriminator(d, ServicerId.MRC))
    twice = pipe(
        df,
        lambda d: apply_servicer_discriminator(d, ServicerId.MRC),
        lambda d: apply_servicer_discriminator(d, ServicerId.MRC),
    )
    assert isinstance(once, DataFrame)
    assert isinstance(twice, DataFrame)
    pd.testing.assert_frame_equal(once, twice)


def test_summary_transform_idempotent_on_output_df() -> None:
    raw = DataFrame([dict.fromkeys(REMIT_SUMMARY_COLUMNS, 2.0)])
    first = prepare_remit_summary(raw, REMIT_DATE)
    # Re-stamping a frame that already contains 'asofdate' produces the same
    # canonical projection (asofdate appended once, no column duplication).
    second = prepare_remit_summary(first.df, REMIT_DATE)
    assert list(second.df.columns) == list(first.df.columns)
    pd.testing.assert_frame_equal(first.df, second.df)
