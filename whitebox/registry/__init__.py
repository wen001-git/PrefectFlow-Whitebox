"""Stage 2 P2.1 — pure validator/sheet/servicer/dataset registry.

This package provides a *foundation only* (no orchestration, no IO, no
validator logic). Engine, sheets, and API layers will consume these
registries in later phases.

Design references:
- docs/stage2/4.0-validator-registry.en.md §§ 2–6
- docs/stage2/5.0-extensibility-spec.en.md § 2 (ServicerId discriminator)
- docs/stage2/11.0-architecture.en.md § 3 (module boundary: no execution)
"""

from __future__ import annotations

from whitebox.registry.base import (
    DatasetSpec,
    DuplicateRegistrationError,
    ServicerSpec,
    SheetSpec,
    UnknownEntryError,
    ValidatorSpec,
)
from whitebox.registry.loader import discover
from whitebox.registry.registry import (
    Registry,
    ValidatorRegistry,
    dataset_registry,
    register_dataset,
    register_servicer,
    register_sheet,
    register_validator,
    servicer_registry,
    sheet_registry,
    validator_registry,
)

__all__ = [
    "DatasetSpec",
    "DuplicateRegistrationError",
    "Registry",
    "ServicerSpec",
    "SheetSpec",
    "UnknownEntryError",
    "ValidatorRegistry",
    "ValidatorSpec",
    "dataset_registry",
    "discover",
    "register_dataset",
    "register_servicer",
    "register_sheet",
    "register_validator",
    "servicer_registry",
    "sheet_registry",
    "validator_registry",
]
