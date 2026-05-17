"""Registry: load + validate validator and sheet YAML metadata.

Loaders return typed dicts; validation errors raise jsonschema.ValidationError
with the JSON path of the offending field. CLI mode prints a tree of all
discovered artifacts.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
VALIDATORS_DIR = ROOT / "whitebox" / "validators"
SHEETS_DIR = ROOT / "sheets"
SCHEMA_DIR = Path(__file__).parent / "schema"
SERVICERS_MANIFEST = ROOT / "docs" / "_status" / "servicers.yaml"


def _load_schema(name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


VALIDATOR_SCHEMA = _load_schema("validator.schema.json")
SHEET_SCHEMA = _load_schema("sheet.schema.json")
SERVICER_SCHEMA = _load_schema("servicer.schema.json")


@dataclass
class Servicer:
    id: str
    display_name: str
    status: str  # done | in-progress | pending-analysis
    sheets_count: int
    stage1_doc: str
    stage2_system: str
    placeholder_doc: str | None
    notes: str = ""


@dataclass
class Validator:
    path: Path
    data: dict[str, Any]
    sql: str | None = None

    @property
    def id(self) -> str:
        return str(self.data["id"])


@dataclass
class Sheet:
    path: Path
    data: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.data["sheet"])

    @property
    def columns(self) -> dict[str, dict[str, Any]]:
        cols: dict[str, dict[str, Any]] = self.data.get("columns", {})
        return cols


def load_servicers(
    manifest: Path = SERVICERS_MANIFEST,
    validators_dir: Path = VALIDATORS_DIR,
    sheets_dir: Path = SHEETS_DIR,
) -> tuple[dict[str, Servicer], list[str]]:
    """Load servicer-status manifest and cross-check against on-disk state."""
    if not manifest.exists():
        return {}, [f"{manifest}: servicer-status manifest is missing"]
    data = _load_yaml(manifest)
    errs = _validate(data, SERVICER_SCHEMA, manifest)
    if errs:
        return {}, errs

    servicers: dict[str, Servicer] = {}
    for entry in data.get("servicers", []):
        sid = entry["id"]
        if sid in servicers:
            errs.append(f"{manifest}: duplicate servicer id '{sid}'")
            continue
        servicers[sid] = Servicer(
            id=sid,
            display_name=entry["display_name"],
            status=entry["status"],
            sheets_count=entry["sheets_count"],
            stage1_doc=entry["stage1_doc"],
            stage2_system=entry["stage2_system"],
            placeholder_doc=entry.get("placeholder_doc"),
            notes=entry.get("notes", ""),
        )

    docs_root = ROOT / "docs"
    for s in servicers.values():
        if s.status == "pending-analysis":
            if not s.placeholder_doc:
                errs.append(
                    f"{manifest}: servicer '{s.id}' is pending-analysis but "
                    f"has no placeholder_doc"
                )
            else:
                ph = ROOT / s.placeholder_doc
                if not ph.exists():
                    errs.append(
                        f"{manifest}: servicer '{s.id}' placeholder_doc "
                        f"'{s.placeholder_doc}' does not exist"
                    )
            # pending servicers must NOT have validator/sheet YAMLs yet
            val_dir = validators_dir / s.id
            if val_dir.exists() and any(val_dir.glob("*.yaml")):
                try:
                    rel = val_dir.relative_to(ROOT)
                except ValueError:
                    rel = val_dir
                errs.append(
                    f"{manifest}: servicer '{s.id}' is pending-analysis but "
                    f"has validator YAMLs under {rel}"
                )
            stray_sheets = list(sheets_dir.glob(f"{s.id.upper()}_*.yaml"))
            if stray_sheets:
                errs.append(
                    f"{manifest}: servicer '{s.id}' is pending-analysis but "
                    f"has sheet YAMLs: "
                    f"{[p.name for p in stray_sheets]}"
                )
        elif s.status in ("done", "in-progress"):
            if s.placeholder_doc:
                errs.append(
                    f"{manifest}: servicer '{s.id}' is {s.status} but still "
                    f"references a placeholder_doc; clear it (set to null)"
                )
    return servicers, errs


@dataclass
class Registry:
    validators: dict[str, Validator] = field(default_factory=dict)
    sheets: dict[str, Sheet] = field(default_factory=dict)
    servicers: dict[str, Servicer] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return data


def _validate(data: dict[str, Any], schema: dict[str, Any], path: Path) -> list[str]:
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for err in validator.iter_errors(data):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {loc}: {err.message}")
    return errors


def load_validator(path: Path) -> tuple[Validator | None, list[str]]:
    data = _load_yaml(path)
    errs = _validate(data, VALIDATOR_SCHEMA, path)
    if errs:
        return None, errs
    sql_file = data.get("sql_file")
    sql: str | None = None
    if sql_file:
        sql_path = (path.parent / sql_file).resolve()
        if not sql_path.exists():
            errs.append(f"{path}: sql_file '{sql_file}' does not exist")
            return None, errs
        sql = sql_path.read_text(encoding="utf-8")
    return Validator(path=path, data=data, sql=sql), []


def load_sheet(path: Path) -> tuple[Sheet | None, list[str]]:
    data = _load_yaml(path)
    errs = _validate(data, SHEET_SCHEMA, path)
    if errs:
        return None, errs
    return Sheet(path=path, data=data), []


def load_all(
    validators_dir: Path = VALIDATORS_DIR,
    sheets_dir: Path = SHEETS_DIR,
    servicers_manifest: Path = SERVICERS_MANIFEST,
) -> Registry:
    reg = Registry()
    for yml in sorted(validators_dir.rglob("*.yaml")):
        v, errs = load_validator(yml)
        if v is not None:
            if v.id in reg.validators:
                reg.errors.append(f"{yml}: duplicate validator id '{v.id}'")
            else:
                reg.validators[v.id] = v
        reg.errors.extend(errs)
    for yml in sorted(sheets_dir.glob("*.yaml")):
        s, errs = load_sheet(yml)
        if s is not None:
            if s.name in reg.sheets:
                reg.errors.append(f"{yml}: duplicate sheet name '{s.name}'")
            else:
                reg.sheets[s.name] = s
        reg.errors.extend(errs)
    # Cross-checks
    for s in reg.sheets.values():
        for vid in s.data.get("producing_validators", []):
            if vid not in reg.validators:
                reg.errors.append(
                    f"{s.path}: producing_validators references unknown id '{vid}'"
                )
        for col_name, col in s.columns.items():
            rv = col.get("related_validator")
            if rv and rv not in reg.validators:
                reg.errors.append(
                    f"{s.path}: columns.{col_name}.related_validator "
                    f"references unknown id '{rv}'"
                )
    # Servicer-status manifest
    servicers, srv_errs = load_servicers(
        manifest=servicers_manifest,
        validators_dir=validators_dir,
        sheets_dir=sheets_dir,
    )
    reg.servicers = servicers
    reg.errors.extend(srv_errs)
    return reg


def main() -> int:
    reg = load_all()
    print(f"Validators: {len(reg.validators)}")
    for vid, v in reg.validators.items():
        print(f"  {vid}  ({v.path.relative_to(ROOT)})")
    print(f"Sheets: {len(reg.sheets)}")
    for sname, s in reg.sheets.items():
        print(f"  {sname}  [{len(s.columns)} cols]  ({s.path.relative_to(ROOT)})")
    print(f"Servicers: {len(reg.servicers)}")
    by_status: dict[str, int] = {}
    for srv in reg.servicers.values():
        by_status[srv.status] = by_status.get(srv.status, 0) + 1
    if by_status:
        breakdown = ", ".join(f"{k}={v}" for k, v in sorted(by_status.items()))
        print(f"  ({breakdown})")
    for srv in reg.servicers.values():
        ph = f"  [placeholder={srv.placeholder_doc}]" if srv.placeholder_doc else ""
        print(
            f"  {srv.id:<11} status={srv.status:<17} "
            f"stage1={srv.stage1_doc:<11} stage2={srv.stage2_system}{ph}"
        )
    if reg.errors:
        print(f"\nErrors ({len(reg.errors)}):", file=sys.stderr)
        for e in reg.errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("\nOK: registry valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
