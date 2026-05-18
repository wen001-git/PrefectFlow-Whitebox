"""Explicit registration of MRC sheets + validators for the engine.

Side-effect imports must happen before :class:`whitebox.engine.Engine`
runs anything. :func:`bootstrap_mrc` is idempotent — it can be called
from CLI startup, the API ``engine_backend`` adapter, and tests
without double-registering anything.

The 5 MRC validators are listed authoritatively here (matches
``docs/mrc/1.0-toc.en.md`` § 5 — corrected to 5, not 4):

1. ``mrc_summary_check``        → ``MRC_Summary_check``
2. ``mrc_check_general_info``   → ``MRC_General_Check``
3. ``mrc_check_adv_balance``    → ``MRC_Advance_Check``
4. ``mrc_service_fee_check``    → ``MRC_ServiceFee_Check``
5. ``mrc_other_check``          → ``MRC_Adv_Info``
"""

from __future__ import annotations

import contextlib

from whitebox.registry import (
    DuplicateRegistrationError,
    register_servicer,
    sheet_registry,
    validator_registry,
)
from whitebox.sheets.mrc import register_mrc_sheets

__all__ = [
    "MRC_VALIDATOR_IDS",
    "bootstrap_mrc",
    "register_mrc_validators",
]


# Authoritative validator-id list, in tab order.
MRC_VALIDATOR_IDS: tuple[str, ...] = (
    "mrc_summary_check",
    "mrc_check_general_info",
    "mrc_check_adv_balance",
    "mrc_service_fee_check",
    "mrc_other_check",
)


def register_mrc_validators(*, override: bool = False) -> None:
    """Import the MRC validator modules so their decorators fire.

    Decorators in ``whitebox.validators.mrc.<name>`` populate
    :data:`whitebox.registry.validator_registry`. Idempotent — if a
    validator is already registered (e.g. via the registry's
    ``discover`` helper) we silently skip it unless ``override`` is
    requested.
    """
    # Local imports trigger decorator side effects. Order matches the
    # XLSX tab order so ``validator_registry.by_servicer("MRC")``
    # returns specs in a stable order even before tab_order sort.
    from whitebox.validators.mrc import (  # noqa: F401
        check_adv_balance,
        check_general_info,
        other_check,
        service_fee_check,
        summary_check,
    )

    if override:
        # Re-fire the decorators by re-registering explicitly via the
        # ``override=True`` flag.
        _force_reregister(
            (summary_check, "mrc_summary_check"),
            (check_general_info, "mrc_check_general_info"),
            (check_adv_balance, "mrc_check_adv_balance"),
            (service_fee_check, "mrc_service_fee_check"),
            (other_check, "mrc_other_check"),
        )


def bootstrap_mrc() -> None:
    """Register the MRC servicer + sheets + validators (idempotent)."""
    with contextlib.suppress(DuplicateRegistrationError):
        register_servicer(id="MRC", display_name="MRC", status="active")

    # Ensure sheet specs are present even if the consumer never
    # imported ``whitebox.sheets`` directly.
    if not all(sheet_registry.contains(sid) for sid in (
        "MRC_Summary_check",
        "MRC_General_Check",
        "MRC_Advance_Check",
        "MRC_ServiceFee_Check",
        "MRC_Adv_Info",
    )):
        register_mrc_sheets()

    register_mrc_validators()


def _force_reregister(*modules: tuple[object, str]) -> None:
    """Re-register validators with ``override=True`` (test helper)."""
    from whitebox.registry import ValidatorSpec

    for mod, validator_id in modules:
        # Each validator module exposes its impl as ``run``.
        fn = getattr(mod, "run")  # noqa: B009
        spec = validator_registry.get(validator_id)
        new_spec = ValidatorSpec(
            id=spec.id,
            servicer=spec.servicer,
            sheet=spec.sheet,
            fn=fn,
            description=spec.description,
            tags=spec.tags,
        )
        validator_registry.register(spec.id, new_spec, override=True)
