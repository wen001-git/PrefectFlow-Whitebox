"""Servicer discriminator — Carrington vs MRC selection.

Cross-ref: docs/stage2/5.0-extensibility-spec.en.md § 2 — onboarding a new
servicer must not require modifying any existing code; the registry alone
selects validators per (servicer, sheet).
"""

from __future__ import annotations

from whitebox.registry import (
    register_servicer,
    register_validator,
    servicer_registry,
    validator_registry,
)


def test_carrington_and_mrc_coexist() -> None:
    register_servicer(id="MRC", display_name="MRC")
    register_servicer(id="CARRINGTON", display_name="Carrington Mortgage Services")

    @register_validator(id="mrc_summary", servicer="MRC", sheet="Summary")
    def _mrc(ctx: object) -> str:
        return "mrc"

    @register_validator(
        id="car_summary", servicer="CARRINGTON", sheet="Summary"
    )
    def _car(ctx: object) -> str:
        return "carrington"

    # Both servicers are registered side-by-side
    assert {s.id for s in servicer_registry} == {"MRC", "CARRINGTON"}

    # Dispatch on (MRC, "Summary") returns only the MRC validator
    mrc_hits = validator_registry.dispatch("MRC", "Summary")
    assert len(mrc_hits) == 1
    assert mrc_hits[0].fn(None) == "mrc"

    # Dispatch on (CARRINGTON, "Summary") returns only the Carrington one
    car_hits = validator_registry.dispatch("CARRINGTON", "Summary")
    assert len(car_hits) == 1
    assert car_hits[0].fn(None) == "carrington"


def test_dispatch_does_not_leak_across_servicers() -> None:
    @register_validator(id="m1", servicer="MRC", sheet="X")
    def _m1(ctx: object) -> None: ...

    @register_validator(id="c1", servicer="CARRINGTON", sheet="X")
    def _c1(ctx: object) -> None: ...

    assert [v.id for v in validator_registry.dispatch("MRC", "X")] == ["m1"]
    assert [v.id for v in validator_registry.dispatch("CARRINGTON", "X")] == ["c1"]


def test_servicer_status_field_supports_pending_analysis() -> None:
    register_servicer(id="ARVEST", display_name="Arvest", status="pending-analysis")
    spec = servicer_registry.get("ARVEST")
    assert spec.status == "pending-analysis"
