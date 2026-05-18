"""Generic `Registry[T]` plus the four module-level singletons + decorators.

The four registries (validator / sheet / servicer / dataset) correspond
1:1 with docs/stage2/4.0-validator-registry.en.md § 2.

This module performs **no** IO, **no** validator dispatch, and **no**
hard-coded servicer branching. It only stores specs and answers lookup
questions. The engine layer will consume it later.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

from whitebox.registry.base import (
    DatasetSpec,
    DuplicateRegistrationError,
    ServicerSpec,
    SheetSpec,
    UnknownEntryError,
    ValidatorSpec,
)

T = TypeVar("T")


class Registry(Generic[T]):
    """Minimal id-keyed registry of frozen spec dataclasses.

    `kind` is used purely for error messages so users see e.g.
    "validator 'V1' already registered" rather than a bare KeyError.
    """

    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._entries: dict[str, T] = {}

    @property
    def kind(self) -> str:
        return self._kind

    def register(self, key: str, spec: T, *, override: bool = False) -> None:
        if key in self._entries and not override:
            raise DuplicateRegistrationError(
                f"{self._kind} {key!r} already registered "
                f"(pass override=True to replace)"
            )
        self._entries[key] = spec

    def get(self, key: str) -> T:
        try:
            return self._entries[key]
        except KeyError as exc:
            raise UnknownEntryError(
                f"{self._kind} {key!r} is not registered"
            ) from exc

    def contains(self, key: str) -> bool:
        return key in self._entries

    def all(self) -> list[T]:
        return list(self._entries.values())

    def ids(self) -> list[str]:
        return list(self._entries.keys())

    def clear(self) -> None:
        """Reset the registry. Intended for test isolation."""
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[T]:
        return iter(self._entries.values())

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and key in self._entries


class ValidatorRegistry(Registry[ValidatorSpec]):
    """Validator registry with servicer/sheet dispatch helpers.

    Dispatch keys follow docs/stage2/4.0-validator-registry.en.md § 2.1:
    the lookup is by validator_id alone (unique across servicers),
    while `by_servicer` / `by_sheet` / `dispatch` cover the engine's
    "give me everything for (servicer, sheet)" use case.
    """

    def __init__(self) -> None:
        super().__init__(kind="validator")

    def by_servicer(self, servicer: str) -> list[ValidatorSpec]:
        return [v for v in self._entries.values() if v.servicer == servicer]

    def by_sheet(self, sheet: str) -> list[ValidatorSpec]:
        return [v for v in self._entries.values() if v.sheet == sheet]

    def dispatch(self, servicer: str, sheet: str) -> list[ValidatorSpec]:
        """Return validators matching both servicer and sheet.

        This is the canonical engine-facing query: zero `if servicer ==
        "MRC"` branches anywhere downstream (docs/stage2/4.0 § 1.2).
        """
        return [
            v for v in self._entries.values()
            if v.servicer == servicer and v.sheet == sheet
        ]


# ---------------------------------------------------------------------------
# Module-level singletons (one per spec type — docs/stage2/4.0 § 6.1)
# ---------------------------------------------------------------------------

validator_registry: ValidatorRegistry = ValidatorRegistry()
sheet_registry: Registry[SheetSpec] = Registry(kind="sheet")
servicer_registry: Registry[ServicerSpec] = Registry(kind="servicer")
dataset_registry: Registry[DatasetSpec] = Registry(kind="dataset")


# ---------------------------------------------------------------------------
# Decorators (docs/stage2/4.0 § 3.1)
# ---------------------------------------------------------------------------

F = TypeVar("F", bound=Callable[..., object])


def register_validator(
    *,
    id: str,
    servicer: str,
    sheet: str,
    description: str = "",
    tags: tuple[str, ...] = (),
    override: bool = False,
) -> Callable[[F], F]:
    """Decorator: register a validator implementation.

    Example::

        @register_validator(id="mrc_check_general_info",
                            servicer="MRC",
                            sheet="MRC_General_Check")
        def mrc_general_info_impl(ctx):
            ...
    """

    def wrap(fn: F) -> F:
        spec = ValidatorSpec(
            id=id,
            servicer=servicer,
            sheet=sheet,
            fn=fn,
            description=description,
            tags=tags,
        )
        validator_registry.register(id, spec, override=override)
        return fn

    return wrap


def register_sheet(
    *,
    id: str,
    servicer: str,
    title: str = "",
    tab_order: int = 0,
    column_count: int = 0,
    override: bool = False,
) -> SheetSpec:
    """Register a sheet definition. Returns the stored spec.

    Called as a plain function (not a decorator) — sheet specs are
    metadata, not callables.
    """
    spec = SheetSpec(
        id=id,
        servicer=servicer,
        title=title,
        tab_order=tab_order,
        column_count=column_count,
    )
    sheet_registry.register(id, spec, override=override)
    return spec


def register_servicer(
    *,
    id: str,
    display_name: str,
    status: str = "active",
    override: bool = False,
) -> ServicerSpec:
    spec = ServicerSpec(id=id, display_name=display_name, status=status)
    servicer_registry.register(id, spec, override=override)
    return spec


def register_dataset(
    *,
    id: str,
    servicer: str,
    source_table: str = "",
    description: str = "",
    override: bool = False,
) -> DatasetSpec:
    spec = DatasetSpec(
        id=id,
        servicer=servicer,
        source_table=source_table,
        description=description,
    )
    dataset_registry.register(id, spec, override=override)
    return spec
