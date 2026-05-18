"""Lookup by id / servicer / sheet."""

from __future__ import annotations

import pytest

from whitebox.registry import (
    UnknownEntryError,
    register_validator,
    validator_registry,
)


def _seed() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="MRC_Summary_check")
    def _v1(ctx: object) -> None: ...

    @register_validator(id="V2", servicer="MRC", sheet="MRC_General_Check")
    def _v2(ctx: object) -> None: ...

    @register_validator(id="V3", servicer="MRC", sheet="MRC_General_Check")
    def _v3(ctx: object) -> None: ...

    @register_validator(id="C1", servicer="CARRINGTON", sheet="CAR_Summary")
    def _c1(ctx: object) -> None: ...


def test_lookup_by_id() -> None:
    _seed()
    assert validator_registry.get("V1").id == "V1"
    assert validator_registry.get("C1").servicer == "CARRINGTON"


def test_lookup_unknown_raises() -> None:
    _seed()
    with pytest.raises(UnknownEntryError):
        validator_registry.get("does-not-exist")


def test_lookup_by_servicer() -> None:
    _seed()
    mrc_ids = sorted(v.id for v in validator_registry.by_servicer("MRC"))
    assert mrc_ids == ["V1", "V2", "V3"]
    car_ids = [v.id for v in validator_registry.by_servicer("CARRINGTON")]
    assert car_ids == ["C1"]
    assert validator_registry.by_servicer("UNKNOWN") == []


def test_lookup_by_sheet() -> None:
    _seed()
    ids = sorted(v.id for v in validator_registry.by_sheet("MRC_General_Check"))
    assert ids == ["V2", "V3"]


def test_ids_and_len() -> None:
    _seed()
    assert len(validator_registry) == 4
    assert set(validator_registry.ids()) == {"V1", "V2", "V3", "C1"}
