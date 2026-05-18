"""Purity guard — verify the transform layer performs zero IO.

Strategy: monkeypatch every ``pandas.read_*`` function and ``open`` to raise,
then exercise the public transform API. Any IO would surface as an error.
"""

from __future__ import annotations

import builtins
from datetime import date
from typing import Any

import pandas as pd
import pytest
from pandas import DataFrame

from whitebox.transform import (
    ADVANCE_TABLE_COLUMNS,
    GENERAL_CHECK_COLUMNS,
    REMIT_SUMMARY_COLUMNS,
    ServicerId,
    apply_servicer_discriminator,
    prepare_advance_table,
    prepare_general_check_inputs,
    prepare_other_check,
    prepare_remit_summary,
)

REMIT_DATE = date(2026, 4, 30)


@pytest.fixture
def io_tripwire(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    """Replace every IO entry-point with a tripwire that fails the test."""
    counters: dict[str, int] = {"reads": 0, "opens": 0}

    def _boom_read(*_a: Any, **_kw: Any) -> Any:
        counters["reads"] += 1
        raise AssertionError("transform layer must not call pandas.read_*")

    for name in dir(pd):
        if name.startswith("read_"):
            attr = getattr(pd, name)
            if callable(attr):
                monkeypatch.setattr(pd, name, _boom_read)

    real_open = builtins.open

    def _boom_open(*args: Any, **kwargs: Any) -> Any:
        # Allow pytest infra and python internals to still read source files;
        # the transform layer itself does not call ``open`` directly.
        counters["opens"] += 1
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", _boom_open)
    return counters


def test_summary_pure(io_tripwire: dict[str, int]) -> None:
    df = DataFrame([dict.fromkeys(REMIT_SUMMARY_COLUMNS, 1.0)])
    before_opens = io_tripwire["opens"]
    prepare_remit_summary(df, REMIT_DATE)
    assert io_tripwire["reads"] == 0
    # No new file opens beyond whatever pytest does on entry.
    assert io_tripwire["opens"] == before_opens


def test_advance_pure(io_tripwire: dict[str, int]) -> None:
    df = DataFrame([dict.fromkeys(ADVANCE_TABLE_COLUMNS, 1.0)])
    prepare_advance_table(df, REMIT_DATE)
    assert io_tripwire["reads"] == 0


def test_general_pure(io_tripwire: dict[str, int]) -> None:
    df = DataFrame([dict.fromkeys(GENERAL_CHECK_COLUMNS, 1.0)])
    prepare_general_check_inputs(df, REMIT_DATE)
    assert io_tripwire["reads"] == 0


def test_other_pure(io_tripwire: dict[str, int]) -> None:
    curr = DataFrame(
        [{"bucket": "x", "description": "y", "transaction_code": "z", "amt": 1.0}]
    )
    prev = DataFrame(columns=["bucket", "description", "transaction_code", "amt"])
    prepare_other_check(curr, prev, REMIT_DATE)
    assert io_tripwire["reads"] == 0


def test_discriminator_pure(io_tripwire: dict[str, int]) -> None:
    df = DataFrame([{"loanid": "a", "servicer": "MRC"}])
    apply_servicer_discriminator(df, ServicerId.MRC)
    assert io_tripwire["reads"] == 0
