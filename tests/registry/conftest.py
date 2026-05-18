"""Shared fixtures: reset registry singletons between tests so order
doesn't matter and decorator side-effects from one test don't leak into
another."""

from __future__ import annotations

import pytest

from whitebox.registry import (
    dataset_registry,
    servicer_registry,
    sheet_registry,
    validator_registry,
)


@pytest.fixture(autouse=True)
def _clear_registries() -> None:
    validator_registry.clear()
    sheet_registry.clear()
    servicer_registry.clear()
    dataset_registry.clear()
