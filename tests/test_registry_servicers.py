"""Tests for the v9.1 servicer-status manifest and registry integration."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.registry import (
    ROOT,
    SERVICERS_MANIFEST,
    load_all,
    load_servicers,
)

EXPECTED_PENDING = {"arvest", "cc5", "selene", "sls", "scattered", "dataflow"}
EXPECTED_DONE = {"carrington", "shellpoint"}
EXPECTED_IN_PROGRESS = {"mrc"}


def test_manifest_exists() -> None:
    assert SERVICERS_MANIFEST.exists(), (
        f"servicer-status manifest is missing at {SERVICERS_MANIFEST}"
    )


def test_manifest_loads_without_errors() -> None:
    servicers, errs = load_servicers()
    assert errs == [], f"servicer manifest validation errors: {errs}"
    assert servicers, "no servicers loaded"


def test_mrc_is_in_progress_with_no_placeholder() -> None:
    servicers, _ = load_servicers()
    assert "mrc" in servicers
    mrc = servicers["mrc"]
    assert mrc.status == "in-progress"
    assert mrc.placeholder_doc is None
    assert mrc.sheets_count == 5
    assert mrc.stage1_doc == "in-progress"


def test_all_pending_servicers_have_existing_placeholder_docs() -> None:
    servicers, _ = load_servicers()
    pending_ids = {sid for sid, s in servicers.items() if s.status == "pending-analysis"}
    assert pending_ids == EXPECTED_PENDING, (
        f"expected pending servicers {EXPECTED_PENDING}, got {pending_ids}"
    )
    for sid in pending_ids:
        ph = servicers[sid].placeholder_doc
        assert ph, f"{sid} pending-analysis but placeholder_doc is empty"
        assert (ROOT / ph).exists(), f"{sid} placeholder_doc {ph} does not exist"


def test_done_servicers_have_no_placeholder() -> None:
    servicers, _ = load_servicers()
    done_ids = {sid for sid, s in servicers.items() if s.status == "done"}
    assert done_ids == EXPECTED_DONE
    for sid in done_ids:
        assert servicers[sid].placeholder_doc is None


def test_full_registry_loads_clean_with_servicers() -> None:
    reg = load_all()
    assert reg.errors == [], f"registry errors: {reg.errors}"
    assert set(reg.servicers) == EXPECTED_PENDING | EXPECTED_DONE | EXPECTED_IN_PROGRESS


def test_pending_servicers_must_not_have_validator_yaml(tmp_path: Path) -> None:
    """Cross-check guard: if a pending servicer gains a validator YAML, it must error."""
    # Build a minimal fake tree where 'arvest' suddenly has a validator yaml.
    fake_validators = tmp_path / "validators"
    (fake_validators / "arvest").mkdir(parents=True)
    (fake_validators / "arvest" / "fake.yaml").write_text("id: arvest_fake\n", encoding="utf-8")
    fake_sheets = tmp_path / "sheets"
    fake_sheets.mkdir()

    _, errs = load_servicers(
        manifest=SERVICERS_MANIFEST,
        validators_dir=fake_validators,
        sheets_dir=fake_sheets,
    )
    assert any("arvest" in e and "validator YAMLs" in e for e in errs), (
        f"expected an arvest validator-YAML error, got: {errs}"
    )
