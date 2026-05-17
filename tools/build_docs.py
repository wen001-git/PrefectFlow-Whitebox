"""End-to-end doc build: validate registry, build column lineage, render MkDocs pages."""

from __future__ import annotations

import sys

from tools import autodoc, build_lineage, registry


def main() -> int:
    print("[1/3] Validating registry...")
    reg = registry.load_all()
    if reg.errors:
        for e in reg.errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"      OK: {len(reg.validators)} validators, {len(reg.sheets)} sheets.")

    print("[2/3] Building column-level lineage (sqlglot)...")
    for vid in reg.validators:
        for msg in build_lineage.build_for_validator(reg, vid):
            print(f"      {msg}")

    print("[3/3] Rendering MkDocs pages...")
    reg = registry.load_all()
    env = autodoc._env()
    for v in reg.validators.values():
        autodoc.render_validator(env, v, reg)
    for s in reg.sheets.values():
        autodoc.render_sheet(env, s, reg)
    autodoc.render_lineage(env, reg)
    autodoc.render_index_pages(reg)
    print(f"      OK: docs generated for {len(reg.validators)} validators, {len(reg.sheets)} sheets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
