"""Decorator-style registration tests (docs/stage2/4.0 § 3.1)."""

from __future__ import annotations

import pytest

from whitebox.registry import (
    DuplicateRegistrationError,
    register_dataset,
    register_servicer,
    register_sheet,
    register_validator,
    validator_registry,
)


def test_decorator_registers_validator() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="MRC_Summary_check")
    def v1(ctx: object) -> object:
        return ctx

    assert "V1" in validator_registry
    spec = validator_registry.get("V1")
    assert spec.servicer == "MRC"
    assert spec.sheet == "MRC_Summary_check"
    assert spec.fn is v1


def test_decorator_returns_original_function() -> None:
    @register_validator(id="V2", servicer="MRC", sheet="MRC_General_Check")
    def v2() -> str:
        return "ok"

    # decorator must return the *same* function, not a wrapper
    assert v2() == "ok"


def test_duplicate_id_raises() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="MRC_Summary_check")
    def _a(ctx: object) -> None:
        return None

    with pytest.raises(DuplicateRegistrationError):
        @register_validator(id="V1", servicer="MRC", sheet="MRC_Summary_check")
        def _b(ctx: object) -> None:
            return None


def test_override_flag_replaces() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="MRC_Summary_check")
    def first(ctx: object) -> str:
        return "first"

    @register_validator(
        id="V1", servicer="MRC", sheet="MRC_Summary_check", override=True
    )
    def second(ctx: object) -> str:
        return "second"

    assert validator_registry.get("V1").fn is second


def test_sheet_servicer_dataset_dedup() -> None:
    register_sheet(id="S1", servicer="MRC", title="t")
    register_servicer(id="MRC", display_name="MRC")
    register_dataset(id="port.portmonth", servicer="MRC")

    for call in (
        lambda: register_sheet(id="S1", servicer="MRC"),
        lambda: register_servicer(id="MRC", display_name="MRC"),
        lambda: register_dataset(id="port.portmonth", servicer="MRC"),
    ):
        with pytest.raises(DuplicateRegistrationError):
            call()
