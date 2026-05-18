"""Loader-based discovery: walks a package and fires decorator side-effects."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

from whitebox.registry import discover, validator_registry


def _write_pkg(root: Path, layout: dict[str, str]) -> None:
    for rel, body in layout.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(body), encoding="utf-8")


def test_discover_imports_public_submodules(tmp_path: Path) -> None:
    pkg_root = tmp_path / "fakevalidators"
    _write_pkg(
        pkg_root,
        {
            "__init__.py": "",
            "alpha.py": """
                from whitebox.registry import register_validator

                @register_validator(id="A1", servicer="MRC", sheet="S1")
                def alpha(ctx):  # noqa: ANN001
                    return ctx
            """,
            "beta.py": """
                from whitebox.registry import register_validator

                @register_validator(id="B1", servicer="MRC", sheet="S2")
                def beta(ctx):  # noqa: ANN001
                    return ctx
            """,
            # underscore-prefixed module must be skipped
            "_skipme.py": """
                from whitebox.registry import register_validator

                @register_validator(id="SKIP", servicer="MRC", sheet="S")
                def skip(ctx):  # noqa: ANN001
                    return ctx
            """,
        },
    )

    sys.path.insert(0, str(tmp_path))
    try:
        imported = discover("fakevalidators")
    finally:
        sys.path.remove(str(tmp_path))
        for mod in list(sys.modules):
            if mod.startswith("fakevalidators"):
                del sys.modules[mod]

    assert "fakevalidators.alpha" in imported
    assert "fakevalidators.beta" in imported
    assert "fakevalidators._skipme" not in imported
    assert "A1" in validator_registry
    assert "B1" in validator_registry
    assert "SKIP" not in validator_registry


def test_discover_swallows_not_implemented(tmp_path: Path) -> None:
    pkg_root = tmp_path / "pendingpkg"
    _write_pkg(
        pkg_root,
        {
            "__init__.py": "",
            "pending.py": "raise NotImplementedError('pending analysis')",
            "ready.py": """
                from whitebox.registry import register_validator

                @register_validator(id="R1", servicer="ARVEST", sheet="X")
                def r1(ctx):  # noqa: ANN001
                    return ctx
            """,
        },
    )

    sys.path.insert(0, str(tmp_path))
    try:
        imported = discover("pendingpkg")
    finally:
        sys.path.remove(str(tmp_path))
        for mod in list(sys.modules):
            if mod.startswith("pendingpkg"):
                del sys.modules[mod]

    assert imported == ["pendingpkg.ready"]
    assert "R1" in validator_registry


def test_discover_on_real_validators_package_is_safe() -> None:
    # The existing whitebox/validators package has no decorated modules yet
    # (Stage 1 living docs — treated as read-only per task scope). Discovery
    # must succeed silently without registering anything.
    imported = discover("whitebox.validators")
    # No exceptions, returns a list (possibly empty).
    assert isinstance(imported, list)
    assert len(validator_registry) == 0


def test_discover_missing_package_raises() -> None:
    with pytest.raises(ModuleNotFoundError):
        discover("definitely.not.a.real.package.xyz")
