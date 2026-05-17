"""Unit tests for tools/freeze_snapshot.py verify subcommand (G2a A4).

All tests use tmp_path and synthetic fixtures — no real MRC data required.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from freeze_snapshot import (  # type: ignore[import]
    _run_verify_checks,
    _compute_expected_logical_names,
    _parse_coverage_md_mrc_owners,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_FAKE_SHA256 = "a" * 64
_FAKE_SHA256_ROWS = "b" * 64

_PLAN_ENTRY_SINGLE = {
    "logical_name": "mrc__my_dataset_abc123",
    "mrc_relevant": True,
    "resolved_paths": ["_export_queries/resolved/mrc__my_dataset_abc123.sql"],
}

_PLAN_ENTRY_FANOUT = {
    "logical_name": "mrc___mrc_adv_info_sql_deadbeef1234",
    "mrc_relevant": True,
    "resolved_paths": [
        "_export_queries/resolved/mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-05-01.sql",
        "_export_queries/resolved/mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-04-01.sql",
    ],
}

_PLAN_ENTRY_NON_MRC = {
    "logical_name": "mrc__other_sql_999999",
    "mrc_relevant": False,
    "resolved_paths": [],
}


def _make_plan_index(tmp_path: Path, entries: list[dict]) -> None:
    plan = {
        "manifest_version": "1.0",
        "entries": entries,
    }
    (tmp_path / "_plan_index.json").write_text(json.dumps(plan), encoding="utf-8")


def _make_sql_files(tmp_path: Path, entries: list[dict]) -> None:
    """Create stub SQL files for every resolved_path in each plan entry."""
    for entry in entries:
        for rpath in entry.get("resolved_paths", []):
            sql_file = tmp_path / rpath
            sql_file.parent.mkdir(parents=True, exist_ok=True)
            bindings_str = "(none)"
            sql_file.write_text(
                f"-- TEMPLATE: {rpath}\n-- BINDINGS: {bindings_str}\n-- GENERATED: 2026-05-17\n\nSELECT 1;\n",
                encoding="utf-8",
            )


def _make_parquet_stub(tmp_path: Path, relative_path: str) -> str:
    """Create a stub 'parquet' file and return its SHA-256."""
    fp = tmp_path / relative_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    content = b"FAKE PARQUET DATA"
    fp.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def _valid_manifest_entry(
    logical_name: str,
    sql_path: str,
    data_path: str,
    sha256_file: str,
) -> dict:
    return {
        "logical_name": logical_name,
        "source": {"type": "redshift", "schema": "port", "table": "portmonth"},
        "export_sql_path": sql_path,
        "filter": {"fctrdt": "2026-05-01"},
        "exported_at": "2026-05-20T10:00:00Z",
        "exporter": "operator",
        "format": "parquet",
        "path": data_path,
        "row_count": 100,
        "column_count": 2,
        "columns": [
            {"name": "col_a", "dtype": "int64"},
            {"name": "col_b", "dtype": "varchar"},
        ],
        "sha256_file": sha256_file,
        "sha256_canonical_rows": _FAKE_SHA256_ROWS,
    }


def _make_manifest(tmp_path: Path, entries: list[dict]) -> None:
    manifest = {"entries": entries}
    (tmp_path / "_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _make_coverage_md(tmp_path: Path, mrc_owners: list[str]) -> None:
    """Create a minimal _coverage.md with the given MRC-relevant owner names."""
    lines = ["# MRC SQL Coverage Report\n", "## SQL strings by source file\n"]
    lines.append("### `flow/remit_validation/mrc_validation.py`\n")
    lines.append("| lines | owner | owner-type | pattern | MRC? | proposed-frozen-as | placeholders | notes |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for owner in mrc_owners:
        lines.append(
            f"| 1 | `{owner}` | function | f-string | ✅ | "
            f"`baselines/mrc/2026-04-30/input_snapshots/parquet/{owner}.parquet` | (none) | auto |"
        )
    md_path = tmp_path / "_export_queries" / "_coverage.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


def test_compute_expected_logical_names_single() -> None:
    names = _compute_expected_logical_names([_PLAN_ENTRY_SINGLE])
    assert names == ["mrc__my_dataset_abc123"]


def test_compute_expected_logical_names_fanout() -> None:
    names = _compute_expected_logical_names([_PLAN_ENTRY_FANOUT])
    assert len(names) == 2
    assert "mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-05-01" in names
    assert "mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-04-01" in names


def test_compute_expected_logical_names_skips_non_mrc() -> None:
    names = _compute_expected_logical_names([_PLAN_ENTRY_NON_MRC])
    assert names == []


def test_parse_coverage_md_mrc_owners(tmp_path: Path) -> None:
    _make_coverage_md(tmp_path, ["mrc_summary_check", "mrc_service_fee_check"])
    coverage_path = tmp_path / "_export_queries" / "_coverage.md"
    owners = _parse_coverage_md_mrc_owners(coverage_path)
    assert "mrc_summary_check" in owners
    assert "mrc_service_fee_check" in owners


# ---------------------------------------------------------------------------
# Integration-style: full check runs
# ---------------------------------------------------------------------------


def _build_valid_fixture(tmp_path: Path) -> dict:
    """Build a complete valid single-dataset fixture in tmp_path.

    Returns the dict of checks for inspection.
    """
    # Plan index
    _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE])
    # SQL file
    _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
    # Coverage md
    _make_coverage_md(tmp_path, ["my_dataset"])
    # Data file
    sha = _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
    # Manifest
    entry = _valid_manifest_entry(
        logical_name="mrc__my_dataset_abc123",
        sql_path="_export_queries/resolved/mrc__my_dataset_abc123.sql",
        data_path="parquet/mrc__my_dataset_abc123.parquet",
        sha256_file=sha,
    )
    _make_manifest(tmp_path, [entry])
    return entry


class TestEmptyFolder:
    """Empty folder → all C1-C6 fail with clear messages."""

    def test_all_core_checks_fail(self, tmp_path: Path) -> None:
        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        ids = {c["check"] for c in checks}
        for cid in ["C1-coverage-parity", "C2-schema-completeness",
                    "C3-file-existence-checksum", "C4-sql-hash-binding",
                    "C5-schema-sanity", "C6-fanout-consistency"]:
            assert cid in ids, f"{cid} not reported"
        # All must fail (manifest doesn't exist)
        for c in checks:
            assert not c["passed"], f"{c['check']} unexpectedly passed on empty folder"
        assert exit_code == 1

    def test_failure_messages_are_informative(self, tmp_path: Path) -> None:
        checks, _ = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        for c in checks:
            assert c["message"], f"{c['check']} has empty message"
            # message should mention manifest
            assert "manifest" in c["message"].lower(), (
                f"{c['check']} message doesn't mention 'manifest': {c['message']}"
            )


class TestValidFixture:
    """Complete valid fixture → all C1-C6 pass."""

    def test_all_pass(self, tmp_path: Path) -> None:
        _build_valid_fixture(tmp_path)
        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        failed = [c for c in checks if not c["passed"]]
        assert not failed, f"Unexpected failures: {[(c['check'], c['message']) for c in failed]}"
        assert exit_code == 0

    def test_check_ids_present(self, tmp_path: Path) -> None:
        _build_valid_fixture(tmp_path)
        checks, _ = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=False)
        ids = {c["check"] for c in checks}
        for cid in ["C1-coverage-parity", "C2-schema-completeness",
                    "C3-file-existence-checksum", "C4-sql-hash-binding",
                    "C5-schema-sanity", "C6-fanout-consistency"]:
            assert cid in ids


class TestTamperedChecksum:
    """Tampered sha256_file → C3 fails."""

    def test_c3_fails_on_tampered_sha(self, tmp_path: Path) -> None:
        _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_coverage_md(tmp_path, ["my_dataset"])
        _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
        bad_sha = "c" * 64  # wrong sha
        entry = _valid_manifest_entry(
            logical_name="mrc__my_dataset_abc123",
            sql_path="_export_queries/resolved/mrc__my_dataset_abc123.sql",
            data_path="parquet/mrc__my_dataset_abc123.parquet",
            sha256_file=bad_sha,
        )
        _make_manifest(tmp_path, [entry])

        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c3 = next(c for c in checks if c["check"] == "C3-file-existence-checksum")
        assert not c3["passed"]
        assert "mismatch" in c3["message"].lower() or any("mismatch" in d.lower() for d in c3["details"])
        assert exit_code == 1


class TestOrphanInManifest:
    """Manifest has a dataset not in plan_index → C1 fails (orphan)."""

    def test_c1_fails_orphan(self, tmp_path: Path) -> None:
        _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_coverage_md(tmp_path, ["my_dataset"])
        sha = _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
        sha2 = _make_parquet_stub(tmp_path, "parquet/mrc__extra_ghost_000000.parquet")
        # Create SQL for orphan too
        ghost_sql = tmp_path / "_export_queries/resolved/mrc__extra_ghost_000000.sql"
        ghost_sql.parent.mkdir(parents=True, exist_ok=True)
        ghost_sql.write_text("SELECT 1;\n", encoding="utf-8")

        entries = [
            _valid_manifest_entry(
                "mrc__my_dataset_abc123",
                "_export_queries/resolved/mrc__my_dataset_abc123.sql",
                "parquet/mrc__my_dataset_abc123.parquet",
                sha,
            ),
            _valid_manifest_entry(
                "mrc__extra_ghost_000000",
                "_export_queries/resolved/mrc__extra_ghost_000000.sql",
                "parquet/mrc__extra_ghost_000000.parquet",
                sha2,
            ),
        ]
        _make_manifest(tmp_path, entries)

        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c1 = next(c for c in checks if c["check"] == "C1-coverage-parity")
        assert not c1["passed"]
        assert "orphan" in c1["message"].lower()
        assert exit_code == 1


class TestMissingFromManifest:
    """Plan has a dataset but manifest doesn't → C1 fails (missing)."""

    def test_c1_fails_missing(self, tmp_path: Path) -> None:
        # Plan has 2 entries; manifest has only 1
        plan_extra = {
            "logical_name": "mrc__second_dataset_xyz789",
            "mrc_relevant": True,
            "resolved_paths": ["_export_queries/resolved/mrc__second_dataset_xyz789.sql"],
        }
        _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE, plan_extra])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_coverage_md(tmp_path, ["my_dataset", "second_dataset"])
        sha = _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
        entry = _valid_manifest_entry(
            "mrc__my_dataset_abc123",
            "_export_queries/resolved/mrc__my_dataset_abc123.sql",
            "parquet/mrc__my_dataset_abc123.parquet",
            sha,
        )
        _make_manifest(tmp_path, [entry])

        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c1 = next(c for c in checks if c["check"] == "C1-coverage-parity")
        assert not c1["passed"]
        assert "missing" in c1["message"].lower()
        assert exit_code == 1


class TestSchemaMismatch:
    """column_count != len(columns) → C5 fails."""

    def test_c5_fails_column_count_mismatch(self, tmp_path: Path) -> None:
        _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_coverage_md(tmp_path, ["my_dataset"])
        sha = _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
        entry = _valid_manifest_entry(
            "mrc__my_dataset_abc123",
            "_export_queries/resolved/mrc__my_dataset_abc123.sql",
            "parquet/mrc__my_dataset_abc123.parquet",
            sha,
        )
        # columns list has 2 entries but column_count = 5
        entry["column_count"] = 5
        _make_manifest(tmp_path, [entry])

        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c5 = next(c for c in checks if c["check"] == "C5-schema-sanity")
        assert not c5["passed"]
        assert "column_count" in c5["message"].lower() or any(
            "column_count" in d.lower() for d in c5["details"]
        )
        assert exit_code == 1


class TestFanoutMissingVariant:
    """Fan-out entry missing one variant → C6 fails."""

    def test_c6_fails_missing_fanout_variant(self, tmp_path: Path) -> None:
        _make_plan_index(tmp_path, [_PLAN_ENTRY_FANOUT])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_FANOUT])
        _make_coverage_md(tmp_path, ["_mrc_adv_info_sql"])

        # Only supply one of the two variants in the manifest
        variant1_name = "mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-05-01"
        sha1 = _make_parquet_stub(
            tmp_path, f"parquet/{variant1_name}.parquet"
        )
        sql1 = (
            "_export_queries/resolved/"
            "mrc___mrc_adv_info_sql_deadbeef1234__fctrdt=2026-05-01.sql"
        )
        entry1 = _valid_manifest_entry(variant1_name, sql1, f"parquet/{variant1_name}.parquet", sha1)
        _make_manifest(tmp_path, [entry1])

        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c6 = next(c for c in checks if c["check"] == "C6-fanout-consistency")
        assert not c6["passed"]
        assert "variant" in c6["message"].lower() or "fan-out" in c6["message"].lower()
        assert exit_code == 1


class TestDuplicateColumnNames:
    """Duplicate column names → C5 fails."""

    def test_c5_fails_duplicate_columns(self, tmp_path: Path) -> None:
        _make_plan_index(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_sql_files(tmp_path, [_PLAN_ENTRY_SINGLE])
        _make_coverage_md(tmp_path, ["my_dataset"])
        sha = _make_parquet_stub(tmp_path, "parquet/mrc__my_dataset_abc123.parquet")
        entry = _valid_manifest_entry(
            "mrc__my_dataset_abc123",
            "_export_queries/resolved/mrc__my_dataset_abc123.sql",
            "parquet/mrc__my_dataset_abc123.parquet",
            sha,
        )
        # Duplicate column names
        entry["columns"] = [
            {"name": "col_a", "dtype": "int64"},
            {"name": "col_a", "dtype": "varchar"},  # duplicate!
        ]
        entry["column_count"] = 2
        _make_manifest(tmp_path, [entry])

        checks, _ = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=True)
        c5 = next(c for c in checks if c["check"] == "C5-schema-sanity")
        assert not c5["passed"]
        assert any("duplicate" in d.lower() for d in c5["details"])


class TestStrictModeChecks:
    """--strict flag enables C7 and C8."""

    def test_c7_c8_absent_without_strict(self, tmp_path: Path) -> None:
        _build_valid_fixture(tmp_path)
        checks, _ = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=False, verbose=False)
        ids = {c["check"] for c in checks}
        assert "C7-bindings-doc" not in ids
        assert "C8-storage-policy" not in ids

    def test_c7_c8_present_with_strict(self, tmp_path: Path) -> None:
        _build_valid_fixture(tmp_path)
        # Provide _bindings.json so C7 has something to check
        bindings = {
            "bindings": {"fctrdt": "2026-05-01"},
            "fanout": {},
        }
        (tmp_path / "_bindings.json").write_text(json.dumps(bindings), encoding="utf-8")
        # Provide .gitignore with required rules
        (tmp_path / ".gitignore").write_text(
            "parquet/\ncsv/\n", encoding="utf-8"
        )
        checks, exit_code = _run_verify_checks(tmp_path, "mrc", "2026-04-30", strict=True, verbose=False)
        ids = {c["check"] for c in checks}
        assert "C7-bindings-doc" in ids
        assert "C8-storage-policy" in ids
        # C7/C8 may pass or fail, but must be present
