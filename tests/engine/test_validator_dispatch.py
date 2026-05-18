"""Validator-dispatch / registry-wiring tests."""

from __future__ import annotations

from whitebox.engine import Engine
from whitebox.engine.mrc_wiring import MRC_VALIDATOR_IDS
from whitebox.engine.runner import SHEET_BUILDERS, dispatch_sheet_builder
from whitebox.registry import validator_registry


def test_all_mrc_validators_registered(engine: Engine) -> None:
    del engine  # bootstrap is the only thing this needs
    specs = validator_registry.by_servicer("MRC")
    ids = {s.id for s in specs}
    for vid in MRC_VALIDATOR_IDS:
        assert vid in ids, f"validator {vid} not registered"


def test_every_validator_targets_a_known_sheet(engine: Engine) -> None:
    del engine
    for vid in MRC_VALIDATOR_IDS:
        spec = validator_registry.get(vid)
        assert spec.sheet in SHEET_BUILDERS, (
            f"validator {vid} targets unknown sheet {spec.sheet!r}"
        )


def test_dispatch_sheet_builder_returns_callable(engine: Engine) -> None:
    del engine
    for sheet_id in SHEET_BUILDERS:
        builder = dispatch_sheet_builder(sheet_id)
        assert callable(builder)
