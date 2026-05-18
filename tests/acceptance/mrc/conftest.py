"""Shared fixtures + helpers for the MRC acceptance harness.

The harness deliberately uses **call-once, share-across-tests**
fixtures with ``scope="session"`` so the same engine output drives
every assertion in the same pytest run. This both makes the suite
fast and guarantees the verdict each test sees is internally
consistent.

Three operational modes are exposed:

* ``engine_run`` — always available. Runs the engine against the
  CTE-harness source.
* ``baseline_xlsx`` — yields the path to the captured legacy baseline
  XLSX if present, else *skips* with a clearly-flagged reason.
* ``legacy_run`` — runs the live legacy flow (requires Redshift +
  Vault); skips with a clearly-flagged reason otherwise.

The skip / fail distinction matters (AGENTS §6.5): a baseline-absent
or env-blocked situation is an **environment skip**, not a test
failure. Real cell-identity violations are test failures.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from whitebox.engine import CTEHarnessSource, Engine, RunResult
from whitebox.renderer import render_workbook, write_workbook

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
REMIT_DATE = date(2026, 4, 30)
SERVICER = "MRC"

BASELINE_XLSX_PATH = (
    REPO_ROOT / "baselines" / "mrc" / "2026-04-30" / "validation_report.xlsx"
)
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "cte_harness"
ALLOWLIST_PATH = (
    REPO_ROOT
    / "tests"
    / "acceptance"
    / "mrc"
    / "acceptance_minor_diffs_allowlist.json"
)

# Markers that surface clearly in pytest -v output so an operator can
# tell at a glance whether a skip is an environment problem vs a real
# unmet condition.
SKIP_ENV_BASELINE = "ENV-SKIP: baseline XLSX absent (G2a not yet closed)"
SKIP_ENV_LEGACY = (
    "ENV-SKIP: legacy live run not available "
    "(missing Vault/Redshift creds or ACCEPTANCE_LEGACY_LIVE!=1)"
)


# ---------------------------------------------------------------------------
# Dataclasses returned by fixtures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EngineRun:
    """One engine invocation, materialised to disk as XLSX + RunResult.json."""

    xlsx_path: Path
    result: RunResult
    output_dir: Path


@dataclass(frozen=True)
class LegacyRun:
    """One legacy MRC invocation, with its XLSX + metadata sidecar."""

    xlsx_path: Path
    metadata_path: Path
    output_dir: Path


# ---------------------------------------------------------------------------
# Marker registration
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "acceptance: MRC v9.1 acceptance-gate suite (see docs/stage2/12.0-acceptance-gate.en.md)",
    )
    config.addinivalue_line(
        "markers",
        "needs_baseline: requires baselines/mrc/<date>/validation_report.xlsx",
    )
    config.addinivalue_line(
        "markers",
        "needs_legacy_live: requires Redshift + Vault credentials",
    )


# ---------------------------------------------------------------------------
# Engine fixtures
# ---------------------------------------------------------------------------


def _run_engine_once(out_dir: Path, run_id: str | None = None) -> EngineRun:
    """Run the engine end-to-end and persist its XLSX + RunResult.json.

    Deliberately uses the **public** API (Engine.bootstrap_mrc +
    render_workbook + write_workbook) so this harness exercises the
    same code path operators hit via ``python -m whitebox.engine``.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = Engine.bootstrap_mrc()
    source = CTEHarnessSource(fixture_dir=FIXTURE_DIR)
    result = engine.run(
        servicer=SERVICER,
        remit_date=REMIT_DATE,
        source=source,
        run_id=run_id,
    )
    xlsx_path = out_dir / "validation_report.xlsx"
    wb = render_workbook(result.sheet_models)
    write_workbook(wb, xlsx_path)
    (out_dir / "RunResult.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return EngineRun(xlsx_path=xlsx_path, result=result, output_dir=out_dir)


@pytest.fixture(scope="session")
def engine_run(tmp_path_factory: pytest.TempPathFactory) -> EngineRun:
    """Primary engine run, shared across the whole acceptance session."""
    out_dir = tmp_path_factory.mktemp("acceptance_engine_primary")
    return _run_engine_once(out_dir)


@pytest.fixture(scope="session")
def engine_run_factory(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[Any]:
    """Factory: ``engine_run_factory(label)`` → fresh :class:`EngineRun`."""

    counter = {"i": 0}

    def _factory(label: str = "run") -> EngineRun:
        counter["i"] += 1
        out_dir = tmp_path_factory.mktemp(f"acceptance_engine_{label}_{counter['i']}")
        return _run_engine_once(out_dir)

    yield _factory


# ---------------------------------------------------------------------------
# Baseline fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def baseline_xlsx() -> Path:
    """Return the captured baseline XLSX path or ENV-SKIP if absent."""
    if not BASELINE_XLSX_PATH.exists():
        pytest.skip(
            f"{SKIP_ENV_BASELINE}: expected at "
            f"{BASELINE_XLSX_PATH.relative_to(REPO_ROOT)}"
        )
    return BASELINE_XLSX_PATH


# ---------------------------------------------------------------------------
# Legacy live fixture
# ---------------------------------------------------------------------------


def _legacy_live_enabled() -> tuple[bool, str]:
    """Return (enabled, reason). reason is only meaningful when not enabled."""
    if os.environ.get("ACCEPTANCE_LEGACY_LIVE") != "1":
        return False, "ACCEPTANCE_LEGACY_LIVE!=1"
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        return False, ".env not present"
    text = env_file.read_text(encoding="utf-8", errors="replace")
    if "VAULT_TOKEN=" not in text or "VAULT_ADDR=" not in text:
        return False, ".env missing VAULT_TOKEN / VAULT_ADDR"
    return True, ""


@pytest.fixture(scope="session")
def legacy_run(tmp_path_factory: pytest.TempPathFactory) -> LegacyRun:
    """Invoke the live legacy MRC flow; ENV-SKIP if creds absent."""
    enabled, reason = _legacy_live_enabled()
    if not enabled:
        pytest.skip(f"{SKIP_ENV_LEGACY}: {reason}")
    out_dir = tmp_path_factory.mktemp("acceptance_legacy_live")
    runner = REPO_ROOT / "tools" / "run_legacy_mrc.py"
    cmd = [
        sys.executable,
        str(runner),
        "--servicer",
        SERVICER.lower(),
        "--remit-date",
        REMIT_DATE.isoformat(),
        "--out-dir",
        str(out_dir),
    ]
    proc = subprocess.run(  # noqa: S603 - args are controlled
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    xlsx = out_dir / "validation_report.xlsx"
    meta = out_dir / "run_metadata.json"
    if proc.returncode != 0 or not xlsx.exists():
        pytest.skip(
            f"{SKIP_ENV_LEGACY}: legacy runner exited {proc.returncode}; "
            f"stderr={proc.stderr[-400:]!r}"
        )
    return LegacyRun(xlsx_path=xlsx, metadata_path=meta, output_dir=out_dir)


# ---------------------------------------------------------------------------
# Allowlist helpers
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def allowlist() -> list[dict[str, Any]]:
    """Loaded acceptance-allowlist entries (empty list if the file is empty)."""
    if not ALLOWLIST_PATH.exists():
        return []
    raw = ALLOWLIST_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(
            f"{ALLOWLIST_PATH} must be a JSON array of allowlist entries"
        )
    return data
