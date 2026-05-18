"""Dispatch by (servicer, sheet) pair — the engine-facing query.

Cross-ref: docs/stage2/4.0-validator-registry.en.md § 1.2 — engine must
not branch on servicer strings; dispatch goes through the registry.
"""

from __future__ import annotations

from whitebox.registry import register_validator, validator_registry


def test_dispatch_mrc_summary_returns_only_matching() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="1.0 Summary")
    def _v1(ctx: object) -> None: ...

    @register_validator(id="V2", servicer="MRC", sheet="2.0 General")
    def _v2(ctx: object) -> None: ...

    @register_validator(id="V3", servicer="CARRINGTON", sheet="1.0 Summary")
    def _v3(ctx: object) -> None: ...

    hits = validator_registry.dispatch("MRC", "1.0 Summary")
    assert [v.id for v in hits] == ["V1"]


def test_dispatch_empty_when_no_match() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="1.0 Summary")
    def _v1(ctx: object) -> None: ...

    assert validator_registry.dispatch("MRC", "missing-sheet") == []
    assert validator_registry.dispatch("OTHER", "1.0 Summary") == []


def test_dispatch_returns_multiple_when_multiple_match() -> None:
    @register_validator(id="V1", servicer="MRC", sheet="MRC_General_Check")
    def _v1(ctx: object) -> None: ...

    @register_validator(id="V2", servicer="MRC", sheet="MRC_General_Check")
    def _v2(ctx: object) -> None: ...

    @register_validator(id="V3", servicer="MRC", sheet="MRC_General_Check")
    def _v3(ctx: object) -> None: ...

    hits = validator_registry.dispatch("MRC", "MRC_General_Check")
    assert sorted(v.id for v in hits) == ["V1", "V2", "V3"]
