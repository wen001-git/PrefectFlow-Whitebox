"""Spec dataclasses + exceptions for the four Stage 2 registries.

Dataclasses are used (not pydantic) to keep the registry dependency-free,
per docs/stage2/11.0-architecture.en.md § 2 (no new pins).

All specs are frozen so registered entries cannot be mutated post-hoc —
the engine treats them as immutable lookup metadata.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class DuplicateRegistrationError(KeyError):
    """Raised when a spec is registered twice without override=True."""


class UnknownEntryError(KeyError):
    """Raised when a lookup is performed for an id not in the registry."""


@dataclass(frozen=True)
class ServicerSpec:
    """Describes a single servicer (the discriminator value).

    Mirrors `ServicerId` enum members in docs/stage2/3.0-data-model.en.md
    § 2.1 — but kept as a plain string id here so this registry stays
    decoupled from the (future) enum and can host onboarding placeholders.
    """

    id: str
    display_name: str
    status: str = "active"           # active | pending-analysis | retired


@dataclass(frozen=True)
class SheetSpec:
    """Describes an output sheet produced by a validator.

    Cross-ref: docs/stage2/4.0-validator-registry.en.md § 5.3 (5 MRC seed
    sheets) and § 2.2 (SheetRegistry shape).
    """

    id: str
    servicer: str
    title: str = ""
    tab_order: int = 0
    column_count: int = 0


@dataclass(frozen=True)
class DatasetSpec:
    """Describes an input dataset (upstream table) used by a servicer.

    Cross-ref: docs/stage2/3.0-data-model.en.md § 2.2 (RawTableSnapshot)
    and docs/mrc/1.1-rawdata.en.md.
    """

    id: str
    servicer: str
    source_table: str = ""
    description: str = ""


@dataclass(frozen=True)
class ValidatorSpec:
    """Describes a single validator implementation.

    Cross-ref: docs/stage2/4.0-validator-registry.en.md § 2.1.

    `fn` is the callable that will eventually accept a `ValidatorContext`
    (B3 § 2.6) and return a `ValidatorResult` (B3 § 2.7). At P2.1 we do
    not pin those signatures — the engine phase will tighten the type.
    """

    id: str
    servicer: str
    sheet: str
    fn: Callable[..., Any]
    description: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
