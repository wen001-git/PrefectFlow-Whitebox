"""Entry-point-style discovery for decorated validators.

Implements docs/stage2/4.0-validator-registry.en.md § 6.2 (import-time
decorator firing). At P2.1 we only walk the `whitebox.validators` package;
the optional `whitebox_plugins` entry-point mechanism (§ 7) is a later
phase.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType


def _iter_submodule_names(package: ModuleType) -> list[str]:
    paths = getattr(package, "__path__", None)
    if paths is None:
        return []
    names: list[str] = []
    for info in pkgutil.walk_packages(paths, prefix=f"{package.__name__}."):
        # Skip dunder / private packages (e.g. _placeholder) to avoid
        # firing test-only modules in production discovery.
        leaf = info.name.rsplit(".", 1)[-1]
        if leaf.startswith("_"):
            continue
        names.append(info.name)
    return names


def discover(package_name: str = "whitebox.validators") -> list[str]:
    """Import every public submodule under ``package_name``.

    Decorator side-effects populate the four singleton registries. Returns
    the list of fully-qualified module names that were successfully
    imported, for diagnostics.

    Modules that raise ``NotImplementedError`` at import (the convention
    for pending-analysis servicers per docs/stage2/4.0 § 6.1) are skipped
    silently — startup must not abort.
    """
    package = importlib.import_module(package_name)
    imported: list[str] = []
    for module_name in _iter_submodule_names(package):
        try:
            importlib.import_module(module_name)
        except NotImplementedError:
            continue
        imported.append(module_name)
    return imported
