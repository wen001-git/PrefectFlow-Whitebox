"""Tests for tools/run_legacy_mrc.py.

All tests run without real credentials, Vault, or Redshift.
They exercise dry-run mode, argument validation, and error paths only.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Make the tools package importable from the test runner.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from run_legacy_mrc import (  # type: ignore[import]
    TOOL_VERSION,
    _mask,
    _write_metadata,
    run,
)

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures / helpers
# ──────────────────────────────────────────────────────────────────────────────

_REMIT_DATE = datetime.date(2026, 4, 30)

_ENV_DEFAULTS: dict[str, str] = {
    "VAULT_ADDR": "https://test-vault.example.com:8200",
    "VAULT_TOKEN": "test-token-not-real",
    "VAULT_REDSHIFT_PATH": "prefect-secret/db/redshift",
    "BUILDENV": "prod",
}


def _write_env(tmp_path: Path, **overrides: str) -> Path:
    """Write a .env file in tmp_path with sensible defaults."""
    env_file = tmp_path / ".env"
    vals = {**_ENV_DEFAULTS, **overrides}
    env_file.write_text(
        "\n".join(f"{k}={v}" for k, v in vals.items()), encoding="utf-8"
    )
    return env_file


def _make_source_repo(tmp_path: Path, *, include_mrc: bool = True) -> Path:
    """Create a minimal fake source-repo directory tree."""
    repo = tmp_path / "FakePrefectFlow"
    repo.mkdir()
    (repo / ".git").mkdir()
    flow_dir = repo / "flow" / "remit_validation"
    flow_dir.mkdir(parents=True)
    (flow_dir / "__init__.py").touch()
    if include_mrc:
        (flow_dir / "mrc_validation.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        # Also create the top-level entrypoint so real-run path checks pass
        (flow_dir / "remit_validation.py").write_text(
            "# stub\n", encoding="utf-8"
        )
    return repo


def _fake_meta(**extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "tool_version": TOOL_VERSION,
        "started_at": "2026-04-30T00:00:00+00:00",
        "finished_at": "2026-04-30T00:01:30+00:00",
        "duration_sec": 90.0,
        "servicer": "mrc",
        "remit_date": "2026-04-30",
        "source_repo_path": "/fake/PrefectFlow",
        "source_repo_sha": "abc123def456abc123",
        "source_repo_dirty": False,
        "python_version": "3.10.0 (fake)",
        "platform": "FakeOS-1.0",
        "redshift": {
            "vault_path": "prefect-secret/db/redshift",
            "user": "us****",
            "cluster": "cl****",
        },
        "output": {
            "xlsx_path": "/fake/out/validation_report.xlsx",
            "sha256": "deadbeef" * 8,
            "size_bytes": 12345,
        },
        "datasets": [
            {"name": "mrc_summary_check", "row_count": 1, "query_sec": None},
            {"name": "mrc_general_check", "row_count": 42, "query_sec": None},
        ],
        "exit_code": 0,
    }
    base.update(extra)
    return base


# ──────────────────────────────────────────────────────────────────────────────
# Test 1 — Dry-run with valid .env → prints plan, exit 0, no Redshift contact
# ──────────────────────────────────────────────────────────────────────────────


def test_dry_run_valid_env_exits_zero_prints_plan(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_file = _write_env(tmp_path)
    repo = _make_source_repo(tmp_path)
    out_dir = tmp_path / "out"

    code = run(
        servicer="mrc",
        remit_date=_REMIT_DATE,
        out_dir=out_dir,
        source_repo=repo,
        dry_run=True,
        env_file=env_file,
    )

    assert code == 0
    captured = capsys.readouterr()
    stdout = captured.out

    # Must announce dry-run mode
    assert "DRY-RUN" in stdout

    # Must print every key path/config item
    assert "VAULT_ADDR" in stdout
    assert "VAULT_REDSHIFT_PATH" in stdout
    assert "test-vault.example.com" in stdout
    assert str(_REMIT_DATE) in stdout
    assert "validation_report.xlsx" in stdout
    assert "run_metadata.json" in stdout

    # Must NOT have touched Redshift: no real run.log produced
    assert not (out_dir / "run.log").exists()
    assert not (out_dir / "run_metadata.json").exists()


# ──────────────────────────────────────────────────────────────────────────────
# Test 2 — Missing .env → exit 2, clear error
# ──────────────────────────────────────────────────────────────────────────────


def test_missing_env_file_returns_exit_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _make_source_repo(tmp_path)
    out_dir = tmp_path / "out"
    missing_env = tmp_path / "does_not_exist.env"

    code = run(
        servicer="mrc",
        remit_date=_REMIT_DATE,
        out_dir=out_dir,
        source_repo=repo,
        dry_run=False,
        env_file=missing_env,
    )

    assert code == 2
    captured = capsys.readouterr()
    err = captured.err.lower()
    # Error message must mention .env or env
    assert ".env" in err or "env" in err


# ──────────────────────────────────────────────────────────────────────────────
# Test 3 — Source-repo path does not exist → exit 3
# ──────────────────────────────────────────────────────────────────────────────


def test_missing_source_repo_returns_exit_3(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_file = _write_env(tmp_path)
    out_dir = tmp_path / "out"
    nonexistent_repo = tmp_path / "no_such_repo"

    code = run(
        servicer="mrc",
        remit_date=_REMIT_DATE,
        out_dir=out_dir,
        source_repo=nonexistent_repo,
        dry_run=False,
        env_file=env_file,
    )

    assert code == 3
    captured = capsys.readouterr()
    err = captured.err.lower()
    assert "source repo" in err or "not found" in err


# ──────────────────────────────────────────────────────────────────────────────
# Test 4 — Source-repo exists but mrc_validation.py missing → exit 3
# ──────────────────────────────────────────────────────────────────────────────


def test_source_repo_missing_mrc_validation_returns_exit_3(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    env_file = _write_env(tmp_path)
    # Repo dir exists but does NOT contain mrc_validation.py
    repo = _make_source_repo(tmp_path, include_mrc=False)
    out_dir = tmp_path / "out"

    code = run(
        servicer="mrc",
        remit_date=_REMIT_DATE,
        out_dir=out_dir,
        source_repo=repo,
        dry_run=False,
        env_file=env_file,
    )

    assert code == 3
    captured = capsys.readouterr()
    err = captured.err.lower()
    assert "mrc_validation" in err or "not found" in err


# ──────────────────────────────────────────────────────────────────────────────
# Test 5 — Metadata sidecar shape is correct (schema validation)
# ──────────────────────────────────────────────────────────────────────────────


def test_metadata_sidecar_shape(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    meta = _fake_meta()
    _write_metadata(out_dir, meta)

    sidecar = out_dir / "run_metadata.json"
    assert sidecar.exists(), "run_metadata.json must be written"

    loaded: dict[str, Any] = json.loads(sidecar.read_text(encoding="utf-8"))

    # Top-level required keys
    required_top = [
        "tool_version",
        "started_at",
        "finished_at",
        "duration_sec",
        "servicer",
        "remit_date",
        "source_repo_path",
        "source_repo_sha",
        "source_repo_dirty",
        "python_version",
        "platform",
        "redshift",
        "output",
        "datasets",
        "exit_code",
    ]
    for key in required_top:
        assert key in loaded, f"Sidecar missing required key: {key!r}"

    # Value assertions
    assert loaded["tool_version"] == TOOL_VERSION
    assert loaded["servicer"] == "mrc"
    assert loaded["remit_date"] == "2026-04-30"
    assert loaded["exit_code"] == 0
    assert isinstance(loaded["source_repo_dirty"], bool)

    # redshift sub-object
    rs = loaded["redshift"]
    assert isinstance(rs, dict)
    assert "vault_path" in rs
    assert "user" in rs
    assert "cluster" in rs
    # Must never contain unmasked credentials
    assert rs["user"] != "" and "****" in rs["user"]

    # output sub-object
    out = loaded["output"]
    assert isinstance(out, dict)
    assert "xlsx_path" in out
    assert "sha256" in out
    assert "size_bytes" in out
    assert isinstance(out["size_bytes"], int)

    # datasets is a list of dicts
    assert isinstance(loaded["datasets"], list)
    for ds in loaded["datasets"]:
        assert "name" in ds
        assert "row_count" in ds

    # duration and timestamps
    assert isinstance(loaded["duration_sec"], (int, float))
    assert loaded["duration_sec"] >= 0


# ──────────────────────────────────────────────────────────────────────────────
# Test 6 — CLI --help works and lists all flags
# ──────────────────────────────────────────────────────────────────────────────


def test_cli_help_lists_all_flags() -> None:
    repo_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        [sys.executable, "tools/run_legacy_mrc.py", "--help"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    assert result.returncode == 0, f"--help exited with {result.returncode}"
    help_text = result.stdout

    expected_flags = [
        "--servicer",
        "--remit-date",
        "--out-dir",
        "--source-repo",
        "--dry-run",
        "--env-file",
    ]
    for flag in expected_flags:
        assert flag in help_text, f"Flag {flag!r} missing from --help output"


# ──────────────────────────────────────────────────────────────────────────────
# Bonus — _mask helper sanity checks
# ──────────────────────────────────────────────────────────────────────────────


def test_mask_helper_hides_secrets() -> None:
    assert _mask(None) == "<not-set>"
    assert _mask("") == "<not-set>"
    assert _mask("ab") == "****"
    assert "****" in _mask("secretpassword")
    # First two chars visible, rest masked
    masked = _mask("mysecret")
    assert masked.startswith("my")
    assert "****" in masked
    # Original value is not fully exposed
    assert "secret" not in masked
