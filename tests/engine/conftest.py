"""Shared fixtures for the engine test pack."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from whitebox.engine import CTEHarnessSource, Engine

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cte_harness"


@pytest.fixture(scope="session")
def fixture_dir() -> Path:
    return FIXTURE_DIR


@pytest.fixture(scope="session")
def cte_source(fixture_dir: Path) -> CTEHarnessSource:
    return CTEHarnessSource(fixture_dir=fixture_dir)


@pytest.fixture(scope="session")
def engine() -> Engine:
    return Engine.bootstrap_mrc()


@pytest.fixture(scope="session")
def remit_date() -> date:
    return date(2026, 4, 30)
