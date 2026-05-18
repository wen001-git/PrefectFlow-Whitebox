"""Runtime guard: refuse to render unless openpyxl matches the pin.

Per ``docs/stage2/11.0-architecture.en.md`` § 2 and ``AGENTS.md`` § 6.13,
cell-identity stability is proven only against ``openpyxl==3.1.5``.
Any other build — even a patch release — voids the contract until a
new ADR + cell-identity re-verification is recorded in ``decisions.md``.
"""

from __future__ import annotations

import openpyxl

PINNED_OPENPYXL_VERSION = "3.1.5"


class RendererVersionError(RuntimeError):
    """Raised when the installed openpyxl differs from the pinned version."""


def ensure_openpyxl_pin(actual_version: str | None = None) -> None:
    """Raise :class:`RendererVersionError` unless openpyxl matches the pin.

    ``actual_version`` is overridable for tests; in production it is read
    from ``openpyxl.__version__``.
    """
    version = actual_version if actual_version is not None else openpyxl.__version__
    if version != PINNED_OPENPYXL_VERSION:
        raise RendererVersionError(
            f"openpyxl=={version} but renderer is pinned to "
            f"openpyxl=={PINNED_OPENPYXL_VERSION}. "
            "Bump policy: per AGENTS.md § 6.13 / docs/stage2/11.0-architecture.en.md § 2, "
            "an ADR in decisions.md plus a full cell-identity re-verification "
            "(tools/compare_validation.py against the frozen MRC baseline) is "
            "required before the pin may move."
        )


__all__ = ["PINNED_OPENPYXL_VERSION", "RendererVersionError", "ensure_openpyxl_pin"]
