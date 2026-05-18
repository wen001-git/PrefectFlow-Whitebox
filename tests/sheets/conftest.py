"""Shared fixtures for sheet-builder tests.

Re-registers MRC sheet specs before each test because some other test
modules (notably ``tests/registry/conftest.py``) call
``sheet_registry.clear()`` autouse, which would otherwise leave the
registry empty when these tests run after a registry test.
"""

from __future__ import annotations

import pytest

from whitebox.registry import sheet_registry
from whitebox.sheets.mrc import register_mrc_sheets


@pytest.fixture(autouse=True)
def _ensure_sheets_registered() -> None:
    sheet_registry.clear()
    register_mrc_sheets()
